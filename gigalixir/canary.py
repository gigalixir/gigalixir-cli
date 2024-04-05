from . import auth
import urllib
import json
import click
from . import presenter
from six.moves.urllib.parse import quote

def get(session, app_name):
    r = session.get('/api/apps/%s/canaries' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def set(session, app_name, canary_name, weight):
    body = {}
    if canary_name != None:
        body["canary"] = canary_name
    if weight != None:
        body["weight"] = weight
    r = session.put('/api/apps/%s/canaries' % (quote(app_name.encode('utf-8'))), json = body)
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def delete(session, app_name, canary_name):
    r = session.delete('/api/apps/%s/canaries/%s' % (quote(app_name.encode('utf-8')), quote(canary_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)
