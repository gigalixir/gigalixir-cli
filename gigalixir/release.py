import requests
from . import auth
from . import presenter
import urllib
import json
import click
from six.moves.urllib.parse import quote

def get(host, app_name):
    r = requests.get('%s/api/apps/%s/releases' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

