import logging
import signal
import os
import urllib
import json
import re
import uuid
import requests
import sys
import subprocess
import time
from .shell import cast, call
from . import app as gigalixir_app
from six.moves.urllib.parse import quote

def observer(ctx, app_name, erlang_cookie=None, ssh_opts=""):
    if not ctx.obj['router'].supports_multiplexing():
        raise Exception("The observer command is not supported on this platform.")

    host = ctx.obj['host']
    r = requests.get('%s/api/apps/%s/observer-commands' % (host, quote(app_name.encode('utf-8'))), headers = {
        'Content-Type': 'application/json',
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        command = json.loads(r.text)["data"]
        get_cookie_command = command["get_cookie"]
        get_node_name_command = command["get_node_name"]

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

    ssh_master_pid = None
    control_path = "/tmp/gigalixir-cm-%s" % uuid.uuid4()
    ssh_opts += " -S %s" % control_path
    try: 
        logging.getLogger("gigalixir-cli").info("Setting up SSH multiplexing master")
        cmd = "".join(["ssh %s" % (ssh_opts), " root@%s -N -M" % (ssh_ip)])
        ssh_master_pid = subprocess.Popen(cmd.split()).pid

        # wait for ssh master to connect
        logging.getLogger("gigalixir-cli").info("Waiting for SSH multiplexing master")
        time.sleep(5)

        logging.getLogger("gigalixir-cli").info("Fetching erlang cookie")
        if erlang_cookie is None:
            ERLANG_COOKIE = gigalixir_app.distillery_eval(host, app_name, ssh_opts, get_cookie_command).strip("'")
        else:
            ERLANG_COOKIE = erlang_cookie
        logging.getLogger("gigalixir-cli").info("Using erlang cookie: %s" % ERLANG_COOKIE)

        logging.getLogger("gigalixir-cli").info("Fetching pod ip")
        node_name = gigalixir_app.distillery_eval(host, app_name, ssh_opts, get_node_name_command)
        # node_name is surrounded with single quotes
        (sname, MY_POD_IP) = node_name.strip("'").split('@')
        logging.getLogger("gigalixir-cli").info("Using pod ip: %s" % MY_POD_IP)
        logging.getLogger("gigalixir-cli").info("Using node name: %s" % sname)
        logging.getLogger("gigalixir-cli").info("Fetching epmd port and app port.")
        output = gigalixir_app.ssh_helper(host, app_name, ssh_opts, True, "--", "epmd", "-names")
        EPMD_PORT=None
        APP_PORT=None
        for line in output.splitlines():
            match = re.match("^epmd: up and running on port (\d+) with data:$", line)
            if match:
                EPMD_PORT = match.groups()[0]
            match = re.match("^name (.+) at port (\d+)$", line)
            if match:
                APP_PORT = match.groups()[1]
        if EPMD_PORT == None:
            raise Exception("EPMD_PORT not found.")
        if APP_PORT == None:
            raise Exception("APP_PORT not found.")

        ensure_port_free(EPMD_PORT)
        ensure_port_free(APP_PORT)

        try:
            logging.getLogger("gigalixir-cli").info("Setting up SSH tunnel for ports %s and %s" % (APP_PORT, EPMD_PORT))
            cmd = "".join(["ssh %s -O forward -L %s" % (ssh_opts, APP_PORT), ":localhost:", "%s -L %s" % (APP_PORT, EPMD_PORT), ":localhost:", "%s root@%s" % (EPMD_PORT, ssh_ip)])

            cast(cmd)
            # no need to route if pod ip is 127.0.0.1
            logging.getLogger("gigalixir-cli").info("Routing %s to 127.0.0.1" % MY_POD_IP)

            ctx.obj['router'].route_to_localhost(MY_POD_IP, EPMD_PORT, APP_PORT)
            name = uuid.uuid4()
            # cmd = "iex --name %(name)s@%(MY_POD_IP)s --cookie %(ERLANG_COOKIE)s --hidden -e ':observer.start()'" % {"name": name, "MY_POD_IP": MY_POD_IP, "ERLANG_COOKIE": ERLANG_COOKIE}
            cmd = "erl -name %(name)s@%(MY_POD_IP)s -setcookie %(ERLANG_COOKIE)s -hidden -run observer" % {"name": name, "MY_POD_IP": MY_POD_IP, "ERLANG_COOKIE": ERLANG_COOKIE}
            logging.getLogger("gigalixir-cli").info("Running observer using: %s" % cmd)
            logging.getLogger("gigalixir-cli").info("")
            logging.getLogger("gigalixir-cli").info("")
            logging.getLogger("gigalixir-cli").info("============")
            logging.getLogger("gigalixir-cli").info("Instructions")
            logging.getLogger("gigalixir-cli").info("============")

            logging.getLogger("gigalixir-cli").info("In the 'Node' menu, click 'Connect Node'" )
            logging.getLogger("gigalixir-cli").info("enter: %(sname)s@%(MY_POD_IP)s" % {"sname": sname, "MY_POD_IP": MY_POD_IP})
            logging.getLogger("gigalixir-cli").info("and press OK.")
            logging.getLogger("gigalixir-cli").info("")
            logging.getLogger("gigalixir-cli").info("")
            cast(cmd)
        finally:
            logging.getLogger("gigalixir-cli").info("Cleaning up route from %s to 127.0.0.1" % MY_POD_IP)
            ctx.obj['router'].unroute_to_localhost(MY_POD_IP)
    finally:
        if ssh_master_pid:
            # Needed because Ctrl-G -> q leaves it orphaned for some reason. is the subprocess
            # not sent a signal on graceful termination?
            logging.getLogger("gigalixir-cli").info("Cleaning up SSH multiplexing master")
            try:
                os.kill(ssh_master_pid, signal.SIGTERM)
            except OSError:
                # race condition if parent process tries to clean up subprocesses at the same
                # time
                pass
        if os.path.exists(control_path):
            logging.getLogger("gigalixir-cli").info("Deleting SSH multiplexing file")
            try:
                os.remove(control_path)
            except OSError:
                # race condition if ssh and we try to clean up the file at the same time
                pass

def ensure_port_free(port):
    try:
        # if the port is in use, then a pid is found, this "succeeds" and continues
        # if the port is free, then a pid is not found, this "fails" and raises a CalledProcessError
        pid = call("lsof -wni tcp:%(port)s -t" % {"port": port})
        # If multiplexing gets supported later, on Windows this command would be: 
        #   pid = call("netstat -p tcp -n | find \"\"\":%(port)s\"\"\" % {"port": port})
        raise Exception("It looks like process %s is using port %s on your local machine. We need this port to be able to connect observer. Please kill this process on your local machine and try again. e.g. `kill %s`" % (pid, port, pid))
    except subprocess.CalledProcessError:
        # success! continue
        pass
