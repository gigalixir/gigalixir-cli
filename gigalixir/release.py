from . import auth
from . import presenter
import urllib
import json
import click
from six.moves.urllib.parse import quote

def get(session, app_name):
    r = session.get('/api/apps/%s/releases' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

