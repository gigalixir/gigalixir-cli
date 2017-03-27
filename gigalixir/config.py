import requests
import json
import click

def get(app_name):
    r = requests.get('http://localhost:4000/api/apps/%s/configs' %app_name, headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        click.echo(json.dumps(data, indent=2, sort_keys=True))

