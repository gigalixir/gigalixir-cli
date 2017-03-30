import requests
import json
import click

def get():
    r = requests.get('http://localhost:4000/api/ssh_keys', headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        click.echo(json.dumps(data, indent=2, sort_keys=True))

def create(key):
    r = requests.post('http://localhost:4000/api/ssh_keys', headers = {
        'Content-Type': 'application/json',
    }, json = {
        "ssh_key": key,
    })
    if r.status_code != 201:
        raise Exception(r.text)

def delete(key_id):
    r = requests.delete('http://localhost:4000/api/ssh_keys/%s' % key_id, headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)
