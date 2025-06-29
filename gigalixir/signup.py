import click
import datetime
import re
import stripe
from . import netrc
from . import user as gigalixir_user

def by_email(ctx):
  env = ctx.obj['env']
  session = ctx.obj['session']

  print("Welcome, let's get you started!")
  print("")
  print("We require a *valid* email address to be on file in case we need to reach you about your applications.")
  print("We promise to not abuse your email address.")
  print("Don't believe us? Read our privacy policy: https://gigalixir.com/privacy-policy")
  print("")
  email = click.prompt('Email')
  (vpn, uuid) = set_email(session, email)
  if vpn:
    handle_vpn(session, uuid)

  print("")
  print("Please check your email for the confirmation code we have sent you.")
  accepted = False
  while not accepted:
    code = click.prompt('Confirmation code')
    accepted = confirm(session, uuid, code)
  print("Thank you for your trust in us.")
  print("")

  print("Now we need a password.")
  accepted = False
  while not accepted:
    password = click.prompt('Password', hide_input=True)
    accepted = set_password(session, uuid, password)
  print("")

  (promo, tier) = select_tier(session, uuid)

  confirm_and_complete(session, uuid, email, tier, promo, env, vpn)

def by_oauth(ctx, provider):
  env = ctx.obj['env']
  session = ctx.obj['session']

  welcome_message()

  (oauth_session, url, uuid) = start_oauth(session, provider)

  # TODO: handle vpn detected (204 response)
  data = gigalixir_user.oauth_process(session, provider, 'signup', url, oauth_session)
  email = data['email']
  print("Thank you for your trust in us.")

  vpn = False
  if 'vpn_detected' in data and data['vpn_detected']:
    vpn = True
    handle_vpn(session, uuid)

  print("")
  (promo, tier) = select_tier(session, uuid)

  confirm_and_complete(session, uuid, email, tier, promo, env, vpn)


def welcome_message():
  print("Welcome, let's get you started!")
  print("")

  print("We require a *valid* email address to be on file in case we need to reach you about your applications.")
  print("We promise to not abuse your email address.")
  print("Don't believe us? Read our privacy policy: https://gigalixir.com/privacy-policy")
  print("")

def start_oauth(session, provider):
  r = session.post('/api/signup', json = { 'oauth': provider })
  if r.status_code != 200:
    raise Exception(r.text)

  data = r.json()['data']
  return (data['session'], data['url'], data['uuid'])

def set_email(session, email):
  r = session.post('/api/signup', json = { 'email': email })
  if r.status_code == 429:
    raise Exception('Too many attempts. Please try again later.')

  if r.status_code == 200:
    return (False, r.json()['data']['uuid'])
  elif r.status_code == 202:
    return (True, r.json()['data']['uuid'])

  raise Exception(r.text)


def confirm(session, uuid, code):
  r = session.post('/api/signup', json = { 'confirmation_code': code, 'uuid': uuid })
  if r.status_code == 429:
    raise Exception('Too many attempts. Please try again later.')

  return r.status_code == 200

def set_password(session, uuid, password):
  r = session.post('/api/signup', json = { 'password': password, 'uuid': uuid })
  if r.status_code != 200:
    print(r.text)
    return False

  return True

def set_cc(session, uuid, stripe_token):
  r = session.post('/api/signup', json = { 'stripe_token': stripe_token, 'uuid': uuid })
  if r.status_code == 429:
    raise Exception('Too many attempts. Please try again later.')

  if r.status_code != 200:
    print(r.text)
    return False

  return True

def finalize(session, uuid, tier):
  r = session.post('/api/signup', json = { 'tier': tier, 'uuid': uuid })
  if r.status_code == 200:
    data = r.json()['data']
    return (data['email'], data['key'])
  elif r.status_code == 202:
    return (None, None)

  raise Exception(r.text)


## input validations
def luhn_check(card_number):
  """Validate credit card number using Luhn algorithm."""
  digits = [int(d) for d in card_number]
  checksum = 0

  # Double every second digit from the right, subtracting 9 if >9
  for i, digit in enumerate(reversed(digits)):
    if i % 2 == 1:
      digit *= 2
      if digit > 9:
        digit -= 9
    checksum += digit

  return checksum % 10 == 0

def validate_credit_card_number(card_number):
  """Ensure card number is valid using regex and Luhn check."""
  card_number = card_number.replace(" ", "")  # Allow spaces for readability
  if not re.fullmatch(r"\d{13,19}", card_number):
    raise click.BadParameter("Credit card number must be 13-19 digits long.")
  if not luhn_check(card_number):
    raise click.BadParameter("Invalid credit card number (failed Luhn check).")
  return card_number

def validate_cvv(cvv):
  """Ensure CVV is numeric and correct length."""
  if not re.fullmatch(r"\d{3,4}", cvv):
    raise click.BadParameter("CVV must be 3 or 4 digits.")
  return cvv

def validate_exp_month(exp_month):
  """Ensure expiration month is valid (1-12)."""
  try:
    month = int(exp_month)
    if 1 <= month <= 12:
      return f"{month:02d}"  # Ensure two-digit format
  except ValueError:
    pass
  raise click.BadParameter("Expiration month must be a number between 1 and 12.")

def validate_exp_year(exp_year):
  """Ensure expiration year is in the future and valid."""
  current_year = datetime.datetime.now().year
  try:
    year = int(exp_year)
    if current_year <= year <= current_year + 20:  # Prevent unrealistic years
      return str(year)
  except ValueError:
    pass
  raise click.BadParameter(f"Expiration year must be {current_year} or later.")

def select_tier(session, uuid):
  promo = add_promo_code(session, uuid)
  print("")

  tier = None
  if promo:
    tier = "STANDARD"
  else:
    tier = prompt_tier()
    print("")

  if tier == "STANDARD":
    accepted = False
    while not accepted:
      card_number = click.prompt("Enter credit card number", type=str, value_proc=validate_credit_card_number)
      cvc = click.prompt("Enter CVV", type=str, value_proc=validate_cvv)
      exp_month = click.prompt("Enter expiration month (MM)", type=str, value_proc=validate_exp_month)
      exp_year = click.prompt("Enter expiration year (YYYY)", type=str, value_proc=validate_exp_year)

      stripe_token = stripe.Token.create(card={ "number": card_number, "exp_month": exp_month, "exp_year": exp_year, "cvc": cvc })

      accepted = set_cc(session, uuid, stripe_token["id"])
    print("")

  return (promo, tier)

def add_promo_code(session, uuid):
  while True:
    promo = click.prompt('Promo code [enter to skip]', default="", show_default=False, type=str)
    if promo == "":
      return None
    else:
      r = session.post('/api/signup', json = { 'promo_code': promo, 'uuid': uuid })

      if r.status_code == 200:
        return r.json()['data']['promo']

      elif r.status_code == 429:
        raise Exception('Too many attempts. Please try again later.')

      print("Invalid promo code")

def prompt_tier():
  print("Which tier would you like to sign up for?")
  print("1. Free")
  print("2. Standard")
  while True:
    value = click.prompt('Tier', type=int)
    if value == 1:
      return "FREE"
    elif value == 2:
      return "STANDARD"

def confirm_and_complete(session, uuid, email, tier, promo, env, vpn):
  print("")
  print("You are about to signup for the %s tier." % tier)
  print("  Email: %s" % email)

  if promo:
    print("  Promo: %s" % promo)
  print("")

  print("By continuing, you agree to our Terms of Service and Privacy Policy.")
  print("  Privacy Policy:   https://gigalixir.com/privacy-policy")
  print("  Terms of Service: https://gigalixir.com/terms-of-service")
  print("")
  if not click.confirm('Do you wish to proceed?', default=True):
    raise Exception("Signup cancelled.")
  (email, key) = finalize(session, uuid, tier)

  if vpn:
    print("")
    print("Thank you for signing up.")
    print("Your account is under review.")
    print("We will notify you via email when the review is completed.")
    print("Please allow up to 24 hours.")
  else:
    print("Welcome to Gigalixir!")
    netrc.update_netrc(email, key, env)

def handle_vpn(session, uuid):
  print("")
  print("We have detected that you are using a VPN. Please disable your VPN and try again.")
  print("")
  print("You can continue the signup process with a manual review.")
  print("Manual reviews can take up to 24 hours.")
  if not click.confirm('Do you wish to proceed with a manual review?', default=True):
    raise Exception("Signup cancelled.")

  print("")
  print("Please provide our team with a brief description of your intended application use case.")
  explanation = click.prompt('Description', type=str)

  r = session.post('/api/signup', json = { 'explanation': explanation, 'uuid': uuid })

  if r.status_code != 200:
    raise Exception(r.text)
