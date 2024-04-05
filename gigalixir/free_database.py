import logging
from . import auth
from . import presenter
import urllib
import json
import click
from six.moves.urllib.parse import quote

def create(session, app_name):
    r = session.post('/api/apps/%s/free_databases' % (quote(app_name.encode('utf-8'))), json = {})
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    data = json.loads(r.text)["data"]
    presenter.echo_json(data)
