import logging
from . import auth
from . import api_exception
from . import presenter
import urllib
import json
import click
from six.moves.urllib.parse import quote
import os
import errno

def get(session, app_name):
    r = session.get('/api/apps/%s/databases' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise api_exception.ApiException(r)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def get_read_replicas(session, app_name, database_id):
    r = session.get('/api/apps/%s/databases/%s/read_replicas' % (quote(app_name.encode('utf-8')), quote(database_id.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise api_exception.ApiException(r)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def psql(session, app_name):
    r = session.get('/api/apps/%s/databases' % (quote(app_name.encode('utf-8'))))
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
                if e.errno == errno.ENOENT:
                    raise Exception("Sorry, we could not find psql. Try installing it and try again.")
                else:
                    raise

def create(session, app_name, size, cloud=None, region=None):
    body = {
        "size": size
    }
    if cloud != None:
        body["cloud"] = cloud
    if region != None:
        body["region"] = region
    r = session.post('/api/apps/%s/databases' % (quote(app_name.encode('utf-8'))), json = body)
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    logging.getLogger("gigalixir-cli").info("Creating new database.")
    logging.getLogger("gigalixir-cli").info("Please give us a few minutes to provision the new database.")

def create_read_replica(session, app_name, database_id, size):
    body = {}

    if size:
        body['size'] = size

    r = session.post('/api/apps/%s/databases/%s/read_replicas' % (quote(app_name.encode('utf-8')), quote(database_id.encode('utf-8'))), json = body)
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def delete(session, app_name, database_id):
    r = session.delete('/api/apps/%s/databases/%s' % (quote(app_name.encode('utf-8')), quote(database_id.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def scale(session, app_name, database_id, size, high_availability):
    body = {}

    if high_availability in [ 'disabled', 'enabled' ]:
      body['high_availability'] = high_availability
    elif high_availability:
      raise Exception('high_availability must be either "enabled" or "disabled"')

    if scale:
      body['size'] = size

    r = session.put('/api/apps/%s/databases/%s' % (quote(app_name.encode('utf-8')), quote(database_id.encode('utf-8'))), json = body)

    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def backups(session, app_name, database_id):
    r = session.get('/api/apps/%s/databases/%s/backups' % (quote(app_name.encode('utf-8')), quote(database_id.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def restore(session, app_name, database_id, backup_id):
    r = session.post('/api/apps/%s/databases/%s/backups/%s/restore' % (quote(app_name.encode('utf-8')), quote(database_id.encode('utf-8')), quote(backup_id.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)
