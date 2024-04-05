import logging
import stripe
from . import auth
from . import presenter
import urllib
import json
import click

def get(session):
    r = session.get('/api/payment_methods')
    if r.status_code == 404:
        logging.getLogger("gigalixir-cli").info("No payment method found.")
    elif r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def update(session, card_number, card_exp_month, card_exp_year, card_cvc):
    token = stripe.Token.create(
        card={
            "number": card_number,
            "exp_month": card_exp_month,
            "exp_year": card_exp_year,
            "cvc": card_cvc,
        },
    )
    r = session.put('/api/payment_methods', json = {
        "stripe_token": token["id"],
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

