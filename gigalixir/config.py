from . import auth
import urllib
import json
import click
from . import presenter
from six.moves.urllib.parse import quote

def get(session, app_name):
    r = session.get('/api/apps/%s/configs' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def create_multiple(session, app_name, configs, dont_restart):
    r = session.post('/api/apps/%s/configs' % (quote(app_name.encode('utf-8'))), json = {
        "configs": configs,
        "avoid_restart": dont_restart
    })
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def copy(session, src_app_name, dst_app_name):
    r = session.post('/api/apps/%s/configs/copy' % (quote(dst_app_name.encode('utf-8'))), json = {
        "from": src_app_name
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def delete(session, app_name, key):
    r = session.delete('/api/apps/%s/configs' % (quote(app_name.encode('utf-8'))), json = {
        "key": key,
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)
