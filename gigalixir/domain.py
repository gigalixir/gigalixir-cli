import requests
import logging
from . import auth
from . import presenter
import urllib
import json
import click
from six.moves.urllib.parse import quote

def get(host, app_name):
    r = requests.get('%s/api/apps/%s/domains' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def create(host, app_name, fqdn):
    r = requests.post('%s/api/apps/%s/domains' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "fqdn": fqdn,
    })
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    data = json.loads(r.text)["data"]
    cname = data["cname"]
    logging.getLogger("gigalixir-cli").info("Added %s." % fqdn)
    logging.getLogger("gigalixir-cli").info("Create a CNAME record with your DNS provider pointing to %s" % cname)
    logging.getLogger("gigalixir-cli").info("Please give us a few minutes to set up a new TLS certificate.")


def delete(host, app_name, fqdn):
    r = requests.delete('%s/api/apps/%s/domains' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "fqdn": fqdn,
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
