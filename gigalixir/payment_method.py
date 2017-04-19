import logging
import requests
import stripe
from . import auth
import urllib
import json
import click

def get(host):
    r = requests.get('%s/api/payment_methods' % host, headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code == 404:
        logging.getLogger("gigalixir-cli").info("No payment method found.")
    elif r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        click.echo(json.dumps(data, indent=2, sort_keys=True))

def update(host, card_number, card_exp_month, card_exp_year, card_cvc):
    token = stripe.Token.create(
        card={
            "number": card_number,
            "exp_month": card_exp_month,
            "exp_year": card_exp_year,
            "cvc": card_cvc,
        },
    )
    r = requests.put('%s/api/payment_methods' % host, headers = {
        'Content-Type': 'application/json',
    }, json = {
        "stripe_token": token["id"],
    })
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

