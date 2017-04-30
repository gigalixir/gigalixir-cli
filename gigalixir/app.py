import os
import logging
import urllib
import json
import subprocess
import requests
import click
from .shell import cast, call
from . import auth
from contextlib import closing

def get(host):
    r = requests.get('%s/api/apps' % host, headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        data = [{
            "name": datum["unique_name"],
            "size": datum["size"],
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

    body = {}
    if unique_name != None:
        body = {
            "unique_name": unique_name.lower()
        }
    r = requests.post('%s/api/apps' % host, headers = {
        'Content-Type': 'application/json',
    }, json = body)
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        unique_name = data["unique_name"]
        logging.getLogger("gigalixir-cli").info("Created app: %s." % unique_name)

        # create the git remote
        remotes = call('git remote').splitlines()
        if 'gigalixir' in remotes:
            cast('git remote rm gigalixir')
        cast('git remote add gigalixir https://git.gigalixir.com/%s.git/' % unique_name)
        logging.getLogger("gigalixir-cli").info("Added git remote: gigalixir.")
        click.echo(unique_name)

def status(host, app_name):
    r = requests.get('%s/api/apps/%s/status' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        click.echo(json.dumps(data, indent=2, sort_keys=True))

def scale(host, app_name, replicas, size):
    json = {}
    if replicas != None:
        json["replicas"] = replicas
    if size != None:
        json["size"] = size 
    r = requests.put('%s/api/apps/%s/scale' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = json)
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def ssh(host, app_name, command):
    r = requests.get('%s/api/apps/%s/ssh_ip' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        ssh_ip = data["ssh_ip"]
        if command != None and command != "":
            command = "gigalixir_run run %s" % command
        cast("ssh root@%s %s" % (ssh_ip, command))

def restart(host, app_name):
    r = requests.put('%s/api/apps/%s/restart' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def rollback(host, app_name, version):
    if version == None:
        version = second_most_recent_version(host, app_name)
    r = requests.post('%s/api/apps/%s/releases/%s/rollback' % (host, urllib.quote(app_name.encode('utf-8')), urllib.quote(str(version).encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def second_most_recent_version(host, app_name):
    r = requests.get('%s/api/apps/%s/releases' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        if len(data) < 2:
            raise Exception("No release available to rollback to.")
        else:
            return data[1]["version"]

def run(host, app_name, module, function):
    r = requests.post('%s/api/apps/%s/run' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "module": module,
        "function": function
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def logs(host, app_name):
    logging.getLogger("gigalixir-cli").info("Warning: Logging is still in alpha. If you need faster, more reliable logging, consider PaperTrail.")
    logging.getLogger("gigalixir-cli").info("Aggregating and routing logs, this may take a minute.")
    with closing(requests.get('%s/api/apps/%s/logs' % (host, urllib.quote(app_name.encode('utf-8'))), stream=True)) as r:
        if r.status_code != 200:
            if r.status_code == 401:
                raise auth.AuthException()
            raise Exception(r.text)
        else:
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    click.echo(chunk, nl=False)

