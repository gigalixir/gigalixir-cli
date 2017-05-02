import logging
import urllib
import json
import re
import uuid
import requests
import rollbar
import sys
from .shell import cast, call

def observer(ctx, app_name):
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
        logging.getLogger("gigalixir-cli").info("Fetching pod ip and cookie.")
        ERLANG_COOKIE = call(" ".join(["ssh", "root@%s" % ssh_ip, "--", "cat", "/kube-env-vars/ERLANG_COOKIE"]))
        MY_POD_IP = call("ssh root@%s cat /kube-env-vars/MY_POD_IP" % ssh_ip)
        logging.getLogger("gigalixir-cli").info("Fetching epmd port and app port.")
        output = call("ssh root@%s -- epmd -names" % ssh_ip)
        EPMD_PORT = None
        APP_PORT = None
        for line in output.splitlines():
            match = re.match("^epmd: up and running on port (\d+) with data:$", line)
            if match:
                EPMD_PORT = match.groups()[0]
            match = re.match("^name %s at port (\d+)$" % app_name, line)
            if match:
                APP_PORT = match.groups()[0]
        if EPMD_PORT == None:
            raise Exception("EPMD_PORT not found.")
        if APP_PORT == None:
            raise Exception("APP_PORT not found.")
    except:
        logging.getLogger("gigalixir-cli").error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

    try:
        logging.getLogger("gigalixir-cli").info("Setting up SSH tunnel for ports %s and %s" % (APP_PORT, EPMD_PORT))
        cmd = "".join(["ssh -L %s" % APP_PORT, ":localhost:", "%s -L %s" % (APP_PORT, EPMD_PORT), ":localhost:", "%s root@%s -f -N" % (EPMD_PORT, ssh_ip)])
        cast(cmd)
        logging.getLogger("gigalixir-cli").info("Routing %s to 127.0.0.1" % MY_POD_IP)
        ctx.obj['router'].route_to_localhost(MY_POD_IP)
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
        logging.getLogger("gigalixir-cli").info("enter: %(app_name)s@%(MY_POD_IP)s" % {"app_name": app_name, "MY_POD_IP": MY_POD_IP})
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
