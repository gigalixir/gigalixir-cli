import requests
from . import auth
import urllib
import json
import click

def get(host, app_name):
    r = requests.get('%s/api/apps/%s/releases' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        click.echo(json.dumps(list(reversed(data)), indent=2, sort_keys=True))

