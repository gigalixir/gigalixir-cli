import requests
from . import auth
import urllib
import json
import click
from . import presenter
from six.moves.urllib.parse import quote

def get(host, app_name):
    r = requests.get('%s/api/apps/%s/canaries' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def set(host, app_name, canary_name, weight):
    body = {}
    if canary_name != None:
        body["canary"] = canary_name
    if weight != None:
        body["weight"] = weight 
    r = requests.put('%s/api/apps/%s/canaries' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = body)
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def delete(host, app_name, canary_name):
    r = requests.delete('%s/api/apps/%s/canaries/%s' % (host, quote(app_name.encode('utf-8')), quote(canary_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)
