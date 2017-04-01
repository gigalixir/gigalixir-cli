import requests
from . import netrc
import logging
import click
import stripe
import json

def create(host, email, card_number, card_exp_month, card_exp_year, card_cvc, password, accept_terms_of_service_and_privacy_policy):
    if not accept_terms_of_service_and_privacy_policy:
        logging.info("GIGALIXIR Terms of Service: FPO")
        logging.info("GIGALIXIR Privacy Policy: FPO")
        if not click.confirm('Do you accept the Terms of Service and Privacy Policy?'):
            raise Exception("Sorry, you must accept the Terms of Service and Privacy Policy to continue.")

    token = stripe.Token.create(
        card={
            "number": card_number,
            "exp_month": card_exp_month,
            "exp_year": card_exp_year,
            "cvc": card_cvc,
        },
    )
    r = requests.post('%s/api/users' % host, headers = {
        'Content-Type': 'application/json',
    }, json = {
        'email': email,
        'password': password,
        'stripe_token': token["id"],
    })
    if r.status_code != 200:
        raise Exception(r.text)

def change_password(host, email, current_password, new_password):
    r = requests.patch('%s/api/users' % host, auth = (email, current_password), json = {
        "new_password": new_password
    })
    if r.status_code == 401:
        raise Exception("Unauthorized")

    # TODO: might make sense to catch 422 and report errors more nicely than throwing up a stacktrace
    elif r.status_code != 200:
        raise Exception(r.text)

def login(host, email, password, yes):
    r = requests.get('%s/api/login' % host, auth = (email, password))
    if r.status_code == 401:
        raise Exception("Unauthorized")
    elif r.status_code != 200:
        raise Exception(r.text)
    else:
        key = json.loads(r.text)["data"]["key"]
        if yes or click.confirm('Would you like to save your api key to your ~/.netrc file?'):
            netrc.update_netrc(email, key)
        else:
            logging.info('Your api key is %s' % key)
            logging.warn('Many GIGALIXIR CLI commands may not work unless you your ~/.netrc file contains your GIGALIXIR credentials.')

