import requests
import urllib
import json
import click

def get(app_name):
    r = requests.get('http://localhost:4000/api/apps/%s/domains' % urllib.quote(app_name.encode('utf-8')), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        click.echo(json.dumps(data, indent=2, sort_keys=True))

def create(app_name, fqdn):
    r = requests.post('http://localhost:4000/api/apps/%s/domains' % urllib.quote(app_name.encode('utf-8')), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "fqdn": fqdn,
    })
    if r.status_code != 201:
        raise Exception(r.text)

def delete(app_name, fqdn):
    r = requests.delete('http://localhost:4000/api/apps/%s/domains' % (urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "fqdn": fqdn,
    })
    if r.status_code != 200:
        raise Exception(r.text)
