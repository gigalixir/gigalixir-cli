import os
import urllib
import json
import subprocess
import requests
import click
from .shell import cast, call
from contextlib import closing

def get(host):
    r = requests.get('%s/api/apps' % host, headers = {
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

def create(host, unique_name):
    try:
        # check for git folder
        with open(os.devnull, 'w') as FNULL:
            subprocess.check_call('git rev-parse --is-inside-git-dir'.split(), stdout=FNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        raise Exception("You must call this from inside a git repository.")

    unique_name = unique_name.lower()
    r = requests.post('%s/api/apps' % host, headers = {
        'Content-Type': 'application/json',
    }, json = {
        "unique_name": unique_name,
    })
    if r.status_code != 201:
        raise Exception(r.text)
    else:
        # create the git remote
        cast('git remote add gigalixir https://git.gigalixir.com/%s.git/' % unique_name)

def scale(host, app_name, replicas, size):
    r = requests.put('%s/api/apps/%s/scale' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "replicas": replicas,
        "size": int(size * 1000)
    })
    if r.status_code != 200:
        raise Exception(r.text)

def ssh(host, app_name, command):
    r = requests.get('%s/api/apps/%s/ssh_ip' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        ssh_ip = data["ssh_ip"]
        if command != None and command != "":
            command = "/opt/gigalixir/run-cmd %s" % command
        cast("ssh root@%s %s" % (ssh_ip, command))

def restart(host, app_name):
    r = requests.put('%s/api/apps/%s/restart' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)

def rollback(host, app_name, rollback_id):
    if rollback_id == None:
        rollback_id = second_most_recent_rollback_id(host, app_name)
    r = requests.post('%s/api/apps/%s/releases/%s/rollback' % (host, urllib.quote(app_name.encode('utf-8')), urllib.quote(rollback_id.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        raise Exception(r.text)

def second_most_recent_rollback_id(host, app_name):
    r = requests.get('%s/api/apps/%s/releases' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
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

def run(host, app_name, module, function):
    r = requests.put('%s/api/apps/%s/run' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "module": module,
        "function": function
    })
    if r.status_code != 200:
        raise Exception(r.text)

def logs(host, app_name):
    with closing(requests.get('%s/api/apps/%s/logs' % (host, urllib.quote(app_name.encode('utf-8'))), stream=True)) as r:
        if r.status_code != 200:
            raise Exception(r.text)
        else:
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    click.echo(chunk, nl=False)

