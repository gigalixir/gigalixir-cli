import requests
import urllib
import json
import click

def get():
    r = requests.get('http://localhost:4000/api/payment_methods', headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        click.echo(json.dumps(data, indent=2, sort_keys=True))

def update(stripe_token):
    r = requests.put('http://localhost:4000/api/payment_methods', headers = {
        'Content-Type': 'application/json',
    }, json = {
        "stripe_token": stripe_token,
    })
    if r.status_code != 201:
        raise Exception(r.text)

