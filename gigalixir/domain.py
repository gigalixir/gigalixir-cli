import requests
import logging
from . import auth
import urllib
import json
import click

def get(host, app_name):
    r = requests.get('%s/api/apps/%s/domains' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        click.echo(json.dumps(data, indent=2, sort_keys=True))

def create(host, app_name, fqdn):
    r = requests.post('%s/api/apps/%s/domains' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "fqdn": fqdn,
    })
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    logging.getLogger("gigalixir-cli").info("Added %s." % fqdn)
    logging.getLogger("gigalixir-cli").info("Please give us a few minutes to set up a new TLS certificate.")


def delete(host, app_name, fqdn):
    r = requests.delete('%s/api/apps/%s/domains' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "fqdn": fqdn,
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
