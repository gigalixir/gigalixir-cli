from . import auth
from . import netrc
from . import presenter
import logging
import urllib
import click
import stripe
import json
from six.moves.urllib.parse import quote
from time import sleep

def upgrade(session, card_number, card_exp_month, card_exp_year, card_cvc, promo_code):
    token = stripe.Token.create(
        card={
            "number": card_number,
            "exp_month": card_exp_month,
            "exp_year": card_exp_year,
            "cvc": card_cvc,
        },
    )

    body = {"stripe_token": token["id"]}
    if promo_code != None:
        body["promo_code"] = promo_code.upper()

    r = session.post('/api/upgrade', json = body)
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    logging.getLogger("gigalixir-cli").info('Account upgraded.')

def delete(session, email, password):
    r = session.delete('/api/users/destroy', json = {
        'email': email,
        'current_password': password
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    logging.getLogger("gigalixir-cli").info('Account destroyed.')

def logout(env):
    netrc.clear_netrc(env)

def change_password(session, current_password, new_password):
    r = session.patch('/api/users/change_password', json = {
        "current_password": current_password,
        "new_password": new_password
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    data = json.loads(r.text)["data"]
    presenter.echo_json(data)

def login(session, email, password, env, token):
    if not email:
        email = click.prompt('Email')
    if not password:
        password = click.prompt('Password', hide_input=True, confirmation_prompt=False)

    payload = {}
    if token:
        payload["mfa_token"] = token

    r = session.get('/api/login', auth = (quote(email.encode('utf-8')), quote(password.encode('utf-8'))), params=payload)

    if r.status_code != 200:
        if r.status_code == 401:
            raise Exception("Sorry, we could not authenticate you. If you need to reset your password, run `gigalixir account:password:reset --email=%s`." % email)
        elif r.status_code == 303:
            token = click.prompt('Multi-factor Authentication Token')
            login(session, email, password, env, token)
        else:
            raise Exception(r.text)
    else:
        key = json.loads(r.text)["data"]["key"]
        complete_login(email, key, env)

def oauth_login(session, env, provider):
    r = session.post('/api/oauth/%s' % (provider))

    if r.status_code != 201:
        raise Exception(r.text)

    request_url = json.loads(r.text)["data"]["url"]
    oauth_session = json.loads(r.text)["data"]["session"]

    data = oauth_process(session, provider, 'login', request_url, oauth_session)
    email = data["email"]
    key = data["key"]

    complete_login(email, key, env)

def oauth_process(session, provider, action, request_url, oauth_session):
    print('To', action, 'browse to', request_url)

    delay_time = 4
    while True:
        r = session.get('/api/oauth/%s/%s' % (provider, oauth_session))
        if r.status_code == 204:
            if delay_time < 2:
                raise Exception('OAuth process timed out')
            else:
                sleep(delay_time)
                delay_time -= 0.05

        elif r.status_code == 200:
            return json.loads(r.text)["data"]

        else:
            error = json.loads(r.text)["errors"][""]
            raise Exception('Oauth %s %s' % (action, error))

def get_reset_password_token(session, email):
    r = session.put('/api/users/reset_password', json = {"email": email})
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        logging.getLogger("gigalixir-cli").info("Reset password link has been sent to your email.")

def set_email(session, current_password, email):
    r = session.post('/api/users/email', json = {"next_email": email, "current_password": current_password})
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        logging.getLogger("gigalixir-cli").info("Confirmation email sent. Please check your email to continue.")

def reset_password(session, token, password):
    r = session.post('/api/users/reset_password', json = {"token": token, "password": password})
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def get_confirmation_token(session, email):
    r = session.put('/api/users/reconfirm_email', json = {"email": email})
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        logging.getLogger("gigalixir-cli").info("Confirmation email sent.")

def account(session):
    r = session.get('/api/users')
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def complete_login(email, key, env):
    netrc.update_netrc(email, key, env)
    logging.getLogger("gigalixir-cli").info('Logged in as %s.' % email)
