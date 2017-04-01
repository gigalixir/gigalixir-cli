import requests
import urllib
import json
import click

def get(host):
    r = requests.get('%s/api/payment_methods' % host, headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        click.echo(json.dumps(data, indent=2, sort_keys=True))

def update(host, stripe_token):
    r = requests.put('%s/api/payment_methods' % host, headers = {
        'Content-Type': 'application/json',
    }, json = {
        "stripe_token": stripe_token,
    })
    if r.status_code != 201:
        raise Exception(r.text)

