import click
import subprocess
import sys
import re
import uuid

ROLLBAR_POST_CLIENT_ITEM = "2326b83e4a2d4e789dbf981f956a07d5"

@click.group()
def cli():
    pass

def call(cmd):
    return subprocess.check_output(cmd.split()).strip()

def cast(cmd):
    return subprocess.check_call(cmd.split())

def clean_up(MY_POD_IP, EPMD_PORT, APP_PORT):
    click.echo("Cleaning up route from %s to 127.0.0.1" % MY_POD_IP)
    cast("sudo iptables -t nat -D OUTPUT -p all -d %(MY_POD_IP)s -j DNAT --to-destination 127.0.0.1" % {"MY_POD_IP": MY_POD_IP})
    # cast("sudo iptables -t nat -L OUTPUT")
    click.echo("Cleaning up SSH tunnel")
    pid = call("lsof -wni tcp:%(APP_PORT)s -t" % {"APP_PORT": APP_PORT})
    cast("kill -9 %s" % pid)

@cli.command()
@click.argument('app_name')
@click.argument('ssh_ip')
def observer(app_name, ssh_ip):
    """
    launch remote observer to inspect your production nodes
    """
    try:
        click.echo("Fetching pod ip and cookie.")
        ERLANG_COOKIE = call(" ".join(["ssh", "root@%s" % ssh_ip, "--", "cat", "/observer/ERLANG_COOKIE"]))
        MY_POD_IP = call("ssh root@%s cat /observer/MY_POD_IP" % ssh_ip)
        # cast("sudo iptables -t nat -L OUTPUT")
        click.echo("Fetching epmd port and app port.")
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
        click.echo("Unexpected error:", sys.exc_info()[0])
        # TODO: rollbar
        raise

    try:
        click.echo("Setting up SSH tunnel for ports %s and %s" % (APP_PORT, EPMD_PORT))
        cmd = "".join(["ssh -L %s" % APP_PORT, ":localhost:", "%s -L %s" % (APP_PORT, EPMD_PORT), ":localhost:", "%s root@%s -f -N" % (EPMD_PORT, ssh_ip)])
        cast(cmd)
        click.echo("Routing %s to 127.0.0.1" % MY_POD_IP)
        cast("sudo iptables -t nat -A OUTPUT -p all -d %(MY_POD_IP)s -j DNAT --to-destination 127.0.0.1" % {"MY_POD_IP": MY_POD_IP})
        name = uuid.uuid4()
        # cmd = "iex --name %(name)s@%(MY_POD_IP)s --cookie %(ERLANG_COOKIE)s --hidden -e ':observer.start()'" % {"name": name, "MY_POD_IP": MY_POD_IP, "ERLANG_COOKIE": ERLANG_COOKIE}
        cmd = "erl -name %(name)s@%(MY_POD_IP)s -setcookie %(ERLANG_COOKIE)s -hidden -run observer" % {"name": name, "MY_POD_IP": MY_POD_IP, "ERLANG_COOKIE": ERLANG_COOKIE}
        click.echo("Running observer using: %s" % cmd)
        click.echo("In the 'Node' menu, click 'Connect Node'" )
        click.echo("Enter: %(app_name)s@%(MY_POD_IP)s" % {"app_name": app_name, "MY_POD_IP": MY_POD_IP})
        cast(cmd)
    except:
        click.echo("Unexpected error: %s" % sys.exc_info()[0])
        # TODO: rollbar
        raise
    finally:
        clean_up(MY_POD_IP, EPMD_PORT, APP_PORT)

