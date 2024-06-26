from . import auth
from . import presenter
import urllib
import json
import click

def get(session):
    r = session.get('/api/invoices')
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

