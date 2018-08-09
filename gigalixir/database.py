import requests
import logging
from . import auth
from . import presenter
import urllib
import json
import click
from six.moves.urllib.parse import quote

def get(host, app_name):
    r = requests.get('%s/api/apps/%s/databases' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def create(host, app_name, size):
    r = requests.post('%s/api/apps/%s/databases' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "size": size,
    })
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    logging.getLogger("gigalixir-cli").info("Creating new database.")
    logging.getLogger("gigalixir-cli").info("Please give us a few minutes provision the new database.")

def delete(host, app_name, database_id):
    r = requests.delete('%s/api/apps/%s/databases/%s' % (host, quote(app_name.encode('utf-8')), quote(database_id.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def scale(host, app_name, database_id, size):
    r = requests.put('%s/api/apps/%s/databases/%s' % (host, quote(app_name.encode('utf-8')), quote(database_id.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "size": size,
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
