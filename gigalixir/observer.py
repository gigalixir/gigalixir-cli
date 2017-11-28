import logging
import urllib
import json
import re
import uuid
import requests
import rollbar
import sys
import subprocess
from .shell import cast, call
from . import app as gigalixir_app

def observer(ctx, app_name, erlang_cookie=None):
    host = ctx.obj['host']
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

    try:
        logging.getLogger("gigalixir-cli").info("Fetching erlang cookie")
        if erlang_cookie is None:
            # use FOO=$(gigalixir distillery bar eval 'erlang:get_cookie().') instead
            # ERLANG_COOKIE = call(" ".join(["ssh", "root@%s" % ssh_ip, "--", "cat", "/kube-env-vars/ERLANG_COOKIE"]))
            ERLANG_COOKIE = gigalixir_app.distillery_eval(host, app_name, "erlang:get_cookie().")
        else:
            ERLANG_COOKIE = erlang_cookie
        logging.getLogger("gigalixir-cli").info("Using erlang cookie: %s" % ERLANG_COOKIE)

        # use FOO=$(gigalixir distillery bar eval 'node().') instead
        # MY_POD_IP = call("ssh root@%s cat /kube-env-vars/MY_POD_IP" % ssh_ip)
        logging.getLogger("gigalixir-cli").info("Fetching pod ip")
        node_name = gigalixir_app.distillery_eval(host, app_name, "node().")
        # node_name is surrounded with single quotes
        (sname, MY_POD_IP) = node_name.strip("'").split('@')
        logging.getLogger("gigalixir-cli").info("Using pod ip: %s" % MY_POD_IP)
        logging.getLogger("gigalixir-cli").info("Using node name: %s" % sname)
        CUSTOMER_APP_NAME = call("ssh root@%s cat /kube-env-vars/APP" % ssh_ip)
        logging.getLogger("gigalixir-cli").info("Fetching epmd port and app port.")
        output = call("ssh root@%s -- epmd -names" % ssh_ip)
        EPMD_PORT = None
        APP_PORT = None
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
    except:
        logging.getLogger("gigalixir-cli").error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

    ensure_port_free(EPMD_PORT)
    ensure_port_free(APP_PORT)

    try:
        logging.getLogger("gigalixir-cli").info("Setting up SSH tunnel for ports %s and %s" % (APP_PORT, EPMD_PORT))
        cmd = "".join(["ssh -L %s" % APP_PORT, ":localhost:", "%s -L %s" % (APP_PORT, EPMD_PORT), ":localhost:", "%s root@%s -f -N" % (EPMD_PORT, ssh_ip)])
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
    except:
        logging.getLogger("gigalixir-cli").error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)
    finally:
        clean_up(ctx.obj['router'], MY_POD_IP, EPMD_PORT, APP_PORT)

def clean_up(router, MY_POD_IP, EPMD_PORT, APP_PORT):
    logging.getLogger("gigalixir-cli").info("Cleaning up route from %s to 127.0.0.1" % MY_POD_IP)
    router.unroute_to_localhost(MY_POD_IP)
    logging.getLogger("gigalixir-cli").info("Cleaning up SSH tunnel")
    pid = call("lsof -wni tcp:%(APP_PORT)s -t" % {"APP_PORT": APP_PORT})
    cast("kill -9 %s" % pid)

def ensure_port_free(port):
    try:
        # if the port is in use, then a pid is found, this "succeeds" and continues
        # if the port is free, then a pid is not found, this "fails" and raises a CalledProcessError
        pid = call("lsof -wni tcp:%(port)s -t" % {"port": port})
        logging.getLogger("gigalixir-cli").info("It looks like process %s is using port %s. Please kill this process and try again." % (pid, port))
        sys.exit(1)
    except subprocess.CalledProcessError:
        # success! continue
        pass
