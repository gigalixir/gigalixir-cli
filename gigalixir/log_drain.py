from . import auth
from . import presenter
import urllib
import json
import click
from six.moves.urllib.parse import quote

def get(session, app_name):
    r = session.get('/api/apps/%s/drains' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def create(session, app_name, url):
    r = session.post('/api/apps/%s/drains' % (quote(app_name.encode('utf-8'))), json = {
        "url": url,
    })
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def delete(session, app_name, drain_id):
    r = session.delete('/api/apps/%s/drains' % (quote(app_name.encode('utf-8'))), json = {
        "drain_id": drain_id,
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
