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
from . import presenter
from . import ssh_key
from . import git
from contextlib import closing
from six.moves.urllib.parse import quote

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
        presenter.echo_json(data)

def info(host, app_name):
    r = requests.get('%s/api/apps/%s' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def set_git_remote(host, app_name):
    git.check_for_git()

    remotes = call('git remote').splitlines()
    if 'gigalixir' in remotes:
        cast('git remote rm gigalixir')
    cast('git remote add gigalixir https://git.gigalixir.com/%s.git/' % app_name)
    logging.getLogger("gigalixir-cli").info("Set git remote: gigalixir.")

def create(host, unique_name, cloud, region, stack):
    git.check_for_git()

    body = {}
    if unique_name != None:
        body["unique_name"] = unique_name.lower()
    if cloud != None:
        body["cloud"] = cloud
    if region != None:
        body["region"] = region
    if stack != None:
        body["stack"] = stack
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
    r = requests.get('%s/api/apps/%s/status' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def scale(host, app_name, replicas, size):
    body = {}
    if replicas != None:
        body["replicas"] = replicas
    if size != None:
        body["size"] = size 
    r = requests.put('%s/api/apps/%s/scale' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = body)
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def customer_app_name(host, app_name):
    r = requests.get('%s/api/apps/%s/releases/latest' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        return data["customer_app_name"]

def distillery_eval(host, app_name, ssh_opts, expression):
    # capture_output == True as this isn't interactive
    # and we want to return the result as a string rather than
    # print it out to the screen
    return ssh_helper(host, app_name, ssh_opts, True, "gigalixir_run", "distillery_eval", "--", expression)

def distillery_command(host, app_name, ssh_opts, *args):
    ssh(host, app_name, ssh_opts, "gigalixir_run", "shell", "--", "bin/%s" % customer_app_name(host, app_name), *args)

def ssh(host, app_name, ssh_opts, *args):
    # capture_output == False for interactive mode which is
    # used by ssh, remote_console, distillery_command
    ssh_helper(host, app_name, ssh_opts, False, *args)

# if using this from a script, and you want the return
# value in a variable, use capture_output=True
# capture_output needs to be False for remote_console
# and regular ssh to work.
def ssh_helper(host, app_name, ssh_opts, capture_output, *args):
    # verify SSH keys exist
    keys = ssh_key.ssh_keys(host)
    if len(keys) == 0:
        raise Exception("You don't have any ssh keys yet. See `gigalixir account:ssh_keys:add --help`")

    r = requests.get('%s/api/apps/%s/ssh_ip' % (host, quote(app_name.encode('utf-8'))), headers = {
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
            command = " ".join(escaped_args)
            if capture_output:
                return call("ssh %s -t root@%s %s" % (ssh_opts, ssh_ip, command))
            else:
                cast("ssh %s -t root@%s %s" % (ssh_opts, ssh_ip, command))
        else:
            cast("ssh %s -t root@%s" % (ssh_opts, ssh_ip))


def restart(host, app_name):
    r = requests.put('%s/api/apps/%s/restart' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def rollback(host, app_name, version):
    if version == None:
        version = second_most_recent_version(host, app_name)
    r = requests.post('%s/api/apps/%s/releases/%s/rollback' % (host, quote(app_name.encode('utf-8')), quote(str(version).encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def second_most_recent_version(host, app_name):
    r = requests.get('%s/api/apps/%s/releases' % (host, quote(app_name.encode('utf-8'))), headers = {
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

def run(host, app_name, command):
    # runs command in a new container
    r = requests.post('%s/api/apps/%s/run' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = {
        "command": command,
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        click.echo("Starting new container to run: `%s`." % ' '.join(command))
        click.echo("See `gigalixir logs` for any output.")
        click.echo("See `gigalixir ps` for job info.")

def ps_run(host, app_name, ssh_opts, *command):
    # runs command in same container app is running
    ssh(host, app_name, ssh_opts, "gigalixir_run", "shell", "--", *command)

def remote_console(host, app_name, ssh_opts):
    ssh(host, app_name, ssh_opts, "gigalixir_run", "remote_console")

def migrate(host, app_name, migration_app_name, ssh_opts):
    if migration_app_name is None:
        ssh(host, app_name, ssh_opts, "gigalixir_run", "migrate")
    else:
        ssh(host, app_name, ssh_opts, "gigalixir_run", "migrate", "-m", migration_app_name)

def logs(host, app_name, num, no_tail):
    payload = {
        "num_lines": num,
        "follow": not no_tail
    }
    with closing(requests.get('%s/api/apps/%s/logs' % (host, quote(app_name.encode('utf-8'))), stream=True, params=payload)) as r:
        if r.status_code != 200:
            if r.status_code == 401:
                raise auth.AuthException()
            raise Exception(r.text)
        else:
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    click.echo(chunk, nl=False)

def delete(host, app_name):
    r = requests.delete('%s/api/apps/%s' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def set_stack(host, app_name, stack):
    body = {}
    if stack != None:
        body["stack"] = stack
    r = requests.put('%s/api/apps/%s/stack' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    }, json = body)
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

