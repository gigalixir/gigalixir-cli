import os
import pipes
import logging
import urllib
import json
import subprocess
import requests
import click
from .shell import cast, call
from . import auth
from . import ssh_key
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

def set_git_remote(host, app_name):
    remotes = call('git remote').splitlines()
    if 'gigalixir' in remotes:
        cast('git remote rm gigalixir')
    cast('git remote add gigalixir https://git.gigalixir.com/%s.git/' % app_name)
    logging.getLogger("gigalixir-cli").info("Set git remote: gigalixir.")

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

        set_git_remote(host, unique_name)
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

def ssh(host, app_name, *args):
    ssh_helper(host, app_name, False, *args)

# if using this from a script, and you want the return
# value in a variable, use capture_output=True
# capture_output needs to be False for remote_console
# and regular ssh to work.
def ssh_helper(host, app_name, capture_output, *args):
    # verify SSH keys exist
    keys = ssh_key.ssh_keys(host)
    if len(keys) == 0:
        raise Exception("You don't have any ssh keys yet. See `gigalixir add_ssh_key --help`")

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
        if len(args) > 0:
            escaped_args = [pipes.quote(arg) for arg in args]
            command = "gigalixir_run run %s" % " ".join(escaped_args)
            if capture_output:
                return call("ssh -t root@%s %s" % (ssh_ip, command))
            else:
                cast("ssh -t root@%s %s" % (ssh_ip, command))
        else:
            cast("ssh -t root@%s" % (ssh_ip))


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

def distillery_eval(host, app_name, expression):
    return ssh_helper(host, app_name, True, "eval", expression)

def migrate(host, app_name, migration_app_name):
    if migration_app_name == None:
        r = requests.get('%s/api/apps/%s/migrate-command' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
            'Content-Type': 'application/json',
        })
    else:
        r = requests.get('%s/api/apps/%s/migrate-command?migration_app_name=%s' % (host, urllib.quote(app_name.encode('utf-8')), urllib.quote(migration_app_name.encode('utf-8'))), headers = {
            'Content-Type': 'application/json',
        })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        command = json.loads(r.text)["data"]
        try:
            result = distillery_eval(host, app_name, command)
            click.echo("Migration succeeded.")
            click.echo("Migrations run: %s" % result)
        except subprocess.CalledProcessError as e:
            # tell the user why it failed
            click.echo(e.output)
            raise

def logs(host, app_name):
    with closing(requests.get('%s/api/apps/%s/logs' % (host, urllib.quote(app_name.encode('utf-8'))), stream=True)) as r:
        if r.status_code != 200:
            if r.status_code == 401:
                raise auth.AuthException()
            raise Exception(r.text)
        else:
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    click.echo(chunk, nl=False)

def delete(host, app_name):
    r = requests.delete('%s/api/apps/%s' % (host, urllib.quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
