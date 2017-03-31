import os
import urllib
import json
import subprocess
import requests
import click
from .shell import cast, call
from contextlib import closing

def get():
    r = requests.get('http://localhost:4000/api/apps', headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        data = [{
            "name": datum["unique_name"],
            "size": datum["size_m"] / 1000.0,
            "replicas": datum["replicas"],
        } for datum in data]
        click.echo(json.dumps(data, indent=2, sort_keys=True))

def create(unique_name):
    try:
        # check for git folder
        with open(os.devnull, 'w') as FNULL:
            subprocess.check_call('git rev-parse --is-inside-git-dir'.split(), stdout=FNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        raise Exception("You must call this from inside a git repository.")

    unique_name = unique_name.lower()
    r = requests.post('http://localhost:4000/api/apps', headers = {
        'Content-Type': 'application/json',
    }, json = {
        "unique_name": unique_name,
    })
    if r.status_code != 201:
        raise Exception(r.text)
    else:
        # create the git remote
        cast('git remote add gigalixir https://git.gigalixir.com/%s.git/' % unique_name)

def scale(app_name, replicas, size):
    r = requests.put('http://localhost:4000/api/apps/%s/scale' % urllib.quote(app_name.encode('utf-8')), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "replicas": replicas,
        "size": int(size * 1000)
    })
    if r.status_code != 200:
        raise Exception(r.text)

def restart(app_name):
    r = requests.put('http://localhost:4000/api/apps/%s/restart' % urllib.quote(app_name.encode('utf-8')), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)

def rollback(app_name, rollback_id):
    if rollback_id == None:
        rollback_id = second_most_recent_rollback_id(app_name)
    r = requests.post('http://localhost:4000/api/apps/%s/releases/%s/rollback' % (urllib.quote(app_name.encode('utf-8')), urllib.quote(rollback_id.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)

def second_most_recent_rollback_id(app_name):
    r = requests.get('http://localhost:4000/api/apps/%s/releases' % urllib.quote(app_name.encode('utf-8')), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        if len(data) < 2:
            raise Exception("No release available to rollback to.")
        else:
            return data[1]["rollback_id"]

def run(app_name, module, function):
    r = requests.put('http://localhost:4000/api/apps/%s/run' % urllib.quote(app_name.encode('utf-8')), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "module": module,
        "function": function
    })
    if r.status_code != 200:
        raise Exception(r.text)

def logs(app_name):
    with closing(requests.get('http://localhost:4000/api/apps/%s/logs' % urllib.quote(app_name.encode('utf-8')), stream=True)) as r:
        if r.status_code != 200:
            raise Exception(r.text)
        else:
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    click.echo(chunk, nl=False)

