import requests
import logging
from . import auth
from . import presenter
import urllib
import json
import click
from six.moves.urllib.parse import quote
import os

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

def psql(host, app_name):
    r = requests.get('%s/api/apps/%s/databases' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        urls = list(filter(lambda d: d["state"] == "AVAILABLE", data))
        if len(urls) > 1:
            # TODO: allow user to specify database
            click.echo("Found more than one database, using: %s" % urls[0]["id"])
        elif len(urls) < 1:
            click.echo("Sorry, no databases found.")
        else:
            url = urls[0]["url"]
            try:
                os.execlp("psql", "psql", url)
            except OSError as e:
                if e.errno == os.errno.ENOENT:
                    raise Exception("Sorry, we could not find psql. Try installing it and try again.")
                else:
                    raise

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

def backups(host, app_name, database_id):
    r = requests.get('%s/api/apps/%s/databases/%s/backups' % (host, quote(app_name.encode('utf-8')), quote(database_id.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def restore(host, app_name, database_id, backup_id):
    r = requests.post('%s/api/apps/%s/databases/%s/backups/%s/restore' % (host, quote(app_name.encode('utf-8')), quote(database_id.encode('utf-8')), quote(backup_id.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)
