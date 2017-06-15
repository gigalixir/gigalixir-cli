import requests
import logging
from . import auth
import urllib
import json
import click

def get(host, app_name):
    r = requests.get('%s/api/apps/%s/databases' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        click.echo(json.dumps(data, indent=2, sort_keys=True))

def create(host, app_name, size):
    r = requests.post('%s/api/apps/%s/databases' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
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
    r = requests.delete('%s/api/apps/%s/databases/%s' % (host, urllib.quote(app_name.encode('utf-8')), urllib.quote(database_id.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def scale(host, app_name, database_id, size):
    r = requests.put('%s/api/apps/%s/databases/%s' % (host, urllib.quote(app_name.encode('utf-8')), urllib.quote(database_id.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "size": size,
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
