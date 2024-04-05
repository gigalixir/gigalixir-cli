from . import auth
from . import presenter
import urllib
import json
import click
from six.moves.urllib.parse import quote

def get(session, app_name):
    r = session.get('/api/apps/%s/permissions' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def create(session, app_name, email):
    r = session.post('/api/apps/%s/permissions' % (quote(app_name.encode('utf-8'))), json = {
        "email": email,
    })
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def delete(session, app_name, email):
    r = session.delete('/api/apps/%s/permissions' % (quote(app_name.encode('utf-8'))), json = {
        "email": email,
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
