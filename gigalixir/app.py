import os
import re
import shlex
import logging
import urllib
import json
import subprocess
import click
from .shell import cast, call
from . import auth
from . import api_exception
from . import presenter
from . import ssh_key
from . import git
from contextlib import closing
from six.moves.urllib.parse import quote

def get(session):
    r = session.get('/api/apps')
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def info(session, app_name):
    r = session.get('/api/apps/%s' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def set_git_remote(session, app_name):
    git.check_for_git()

    remotes = call('git remote').splitlines()
    if 'gigalixir' in remotes:
        cast('git remote rm gigalixir')
    cast('git remote add gigalixir https://git.gigalixir.com/%s.git/' % app_name)
    logging.getLogger("gigalixir-cli").info("Set git remote: gigalixir.")

def create(session, unique_name, cloud, region, stack):
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
    r = session.post('/api/apps', json = body)
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        unique_name = data["unique_name"]
        logging.getLogger("gigalixir-cli").info("Created app: %s." % unique_name)

        set_git_remote(session, unique_name)
        click.echo(unique_name)

def status(session, app_name):
    r = session.get('/api/apps/%s/status' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise api_exception.ApiException(r)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def kill_pod(session, app_name, pod_name):
    url = '/api/apps/%s/pods/%s' % (quote(app_name.encode('utf-8')), quote(pod_name.encode('utf-8')))
    r = session.delete(url)

    if r.status_code != 202:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def scale(session, app_name, replicas, size):
    body = {}
    if replicas != None:
        body["replicas"] = replicas
    if size != None:
        body["size"] = size
    r = session.put('/api/apps/%s/scale' % (quote(app_name.encode('utf-8'))), json = body)
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def customer_app_name(session, app_name):
    r = session.get('/api/apps/%s/releases/latest' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        return data["customer_app_name"]

def distillery_eval(session, app_name, ssh_opts, ssh_cmd, expression):
    # capture_output == True as this isn't interactive
    # and we want to return the result as a string rather than
    # print it out to the screen
    return ssh_helper(session, app_name, ssh_opts, ssh_cmd, True, "gigalixir_run", "distillery_eval", "--", expression)

def distillery_command(session, app_name, ssh_opts, ssh_cmd, *args):
    ssh(session, app_name, ssh_opts, ssh_cmd, "gigalixir_run", "shell", "--", "bin/%s" % customer_app_name(session, app_name), *args)

def ssh(session, app_name, ssh_opts, ssh_cmd, *args):
    # capture_output == False for interactive mode which is
    # used by ssh, remote_console, distillery_command
    ssh_helper(session, app_name, ssh_opts, ssh_cmd, False, *args)

def ssh_add_identity_option(ssh_opts):
    # use the identity file specified by environment variable
    id_file = os.environ.get("GIGALIXIR_IDENTITY_FILE")
    if id_file and not re.match(r'(^|[\s])-i', ssh_opts):
        return (ssh_opts + " -i " + id_file).strip()

    return ssh_opts

# if using this from a script, and you want the return
# value in a variable, use capture_output=True
# capture_output needs to be False for remote_console
# and regular ssh to work.
def ssh_helper(session, app_name, ssh_opts, ssh_cmd, capture_output, *args):
    # verify SSH keys exist
    keys = ssh_key.ssh_keys(session)
    if len(keys) == 0:
        raise Exception("You don't have any ssh keys yet. See `gigalixir account:ssh_keys:add --help`")

    # use the identity file specified by environment variable
    ssh_opts = ssh_add_identity_option(ssh_opts)

    # if -T and -t are not specified, add the -t option
    if not re.match(r'(^|[\s])-[Tt]', ssh_opts):
        ssh_opts = (ssh_opts + " -t")

    r = session.get('/api/apps/%s/ssh_ip' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        ssh_ip = data["ssh_ip"]
        if len(args) > 0:
            escaped_args = [shlex.quote(arg) for arg in args]
            command = " ".join(escaped_args)
            if capture_output:
                return call("%s %s root@%s %s" % (ssh_cmd, ssh_opts, ssh_ip, command))
            else:
                cast("%s %s root@%s %s" % (ssh_cmd, ssh_opts, ssh_ip, command))
        else:
            cast("%s %s root@%s" % (ssh_cmd, ssh_opts, ssh_ip))


def restart(session, app_name):
    r = session.put('/api/apps/%s/restart' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def rollback(session, app_name, version):
    if version == None:
        version = second_most_recent_version(session, app_name)
    r = session.post('/api/apps/%s/releases/%s/rollback' % (quote(app_name.encode('utf-8')), quote(str(version).encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def second_most_recent_version(session, app_name):
    r = session.get('/api/apps/%s/releases' % (quote(app_name.encode('utf-8'))))
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

def run(session, app_name, command):
    # runs command in a new container
    r = session.post('/api/apps/%s/run' % (quote(app_name.encode('utf-8'))), json = {
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

def ps_run(session, app_name, ssh_opts, ssh_cmd, *command):
    # runs command in same container app is running
    ssh(session, app_name, ssh_opts, ssh_cmd, "gigalixir_run", "shell", "--", *command)

def remote_console(session, app_name, ssh_opts, ssh_cmd):
    ssh(session, app_name, ssh_opts, ssh_cmd, "gigalixir_run", "remote_console")

def migrate(session, app_name, migration_app_name, ssh_opts, ssh_cmd):
    if migration_app_name is None:
        ssh(session, app_name, ssh_opts, ssh_cmd, "gigalixir_run", "migrate")
    else:
        ssh(session, app_name, ssh_opts, ssh_cmd, "gigalixir_run", "migrate", "-m", migration_app_name)

def logs(session, app_name, num, no_tail):
    payload = {
        "num_lines": num,
        "follow": not no_tail
    }
    with closing(session.get('/api/apps/%s/logs' % (quote(app_name.encode('utf-8'))), stream=True, params=payload)) as r:
        if r.status_code != 200:
            if r.status_code == 401:
                raise auth.AuthException()
            raise Exception(r.text)
        else:
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    click.echo(chunk, nl=False)

def delete(session, app_name):
    r = session.delete('/api/apps/%s' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def set_stack(session, app_name, stack):
    body = {}
    if stack != None:
        body["stack"] = stack
    r = session.put('/api/apps/%s/stack' % (quote(app_name.encode('utf-8'))), json = body)
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def maintenance(session, app_name, enable):
    body = { "enable": enable }
    r = session.put('/api/apps/%s/maintenance' % (quote(app_name.encode('utf-8'))), json = body)
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)
