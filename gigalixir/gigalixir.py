import click
import requests
import getpass
import stripe
import subprocess
import sys
import re
import uuid
import rollbar
import logging
import json
import netrc
import os

# TODO: replace localhost:4000 with api.gigalixir.com
# TODO: remove localhost from .netrc file

class LinuxRouter(object):
    def route_to_localhost(self, ip):
        # cast("sudo iptables -t nat -L OUTPUT")
        cast("sudo iptables -t nat -A OUTPUT -p all -d %(ip)s -j DNAT --to-destination 127.0.0.1" % {"ip": ip})
    def unroute_to_localhost(self, ip):
        cast("sudo iptables -t nat -D OUTPUT -p all -d %(ip)s -j DNAT --to-destination 127.0.0.1" % {"ip": ip})
        # cast("sudo iptables -t nat -L OUTPUT")

class DarwinRouter(object):
    def route_to_localhost(self, ip):
        """
        It's not great that we use "from any to any". It would be better to use
        from any to 10.244.7.124, but when I do that, erl fails to startup with
        Protocol 'inet_tcp': register/listen error: etimedout
        My guess is, it's trying to find epmd to register itself, but can't due to
        something in this file.
        """
        ps = subprocess.Popen(('echo', """
rdr pass on lo0 inet proto tcp from any to any port 4369 -> 127.0.0.1 port 4369
rdr pass on lo0 inet proto tcp from any to 10.244.7.124 port 36606 -> 127.0.0.1 port 36606
"""), stdout=subprocess.PIPE)
        subprocess.call(('sudo', 'pfctl', '-ef', '-'), stdin=ps.stdout)
        ps.wait()
        cast("sudo ifconfig lo0 10.244.7.124 netmask 255.255.255.255 alias")
        
    def unroute_to_localhost(self, ip):
        cast("sudo ifconfig lo0 10.244.7.124 netmask 255.255.255.255 -alias")
        subprocess.call("sudo pfctl -ef /etc/pf.conf".split())

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {}
    logging.basicConfig(format='%(message)s', level = logging.INFO)
    ROLLBAR_POST_CLIENT_ITEM = "6fb30e5647474decb3fc8f3175e1dfca"
    rollbar.init(ROLLBAR_POST_CLIENT_ITEM, 'production')

    stripe.api_key = 'pk_test_6tMDkFKTz4N0wIFQZHuzOUyW'
    # stripe.api_key = 'pk_live_45dmSl66k4xLy4X4yfF3RVpd'

    PLATFORM = call("uname -s").lower() # linux or darwin
    if PLATFORM == "linux":
        ctx.obj['router'] = LinuxRouter()
    elif PLATFORM == "darwin":
        ctx.obj['router'] = DarwinRouter()
    else:
        raise Exception("Unknown platform: %s" % PLATFORM)

# if you care about the cmd output use call
def call(cmd):
    return subprocess.check_output(cmd.split()).strip()

# if you only care that the cmd succeeded, call this
def cast(cmd):
    return subprocess.check_call(cmd.split())

def clean_up(router, MY_POD_IP, EPMD_PORT, APP_PORT):
    click.echo("Cleaning up route from %s to 127.0.0.1" % MY_POD_IP)
    router.unroute_to_localhost(MY_POD_IP)
    click.echo("Cleaning up SSH tunnel")
    pid = call("lsof -wni tcp:%(APP_PORT)s -t" % {"APP_PORT": APP_PORT})
    cast("kill -9 %s" % pid)

@cli.group()
def create():
    pass

@cli.group()
def edit():
    pass

@edit.command()
@click.argument('email')
@click.option('-p', '--current_password', default=None)
@click.option('-n', '--new_password', default=None)
def user(email, current_password, new_password):
    try:
        while current_password == None or current_password == '':
            current_password = getpass.getpass('Current Password: ')
        while new_password == None or new_password == '':
            new_password = getpass.getpass('New Password: ')
        r = requests.patch('http://localhost:4000/api/users', auth = (email, current_password), json = {
            "new_password": new_password
        })
        if r.status_code == 401:
            logging.error("Unauthorized")

        # TODO: might make sense to catch 422 and report errors more nicely than throwing up a stacktrace
        elif r.status_code != 200:
            raise Exception(r.text)
    except:
        click.echo("Unexpected error: %s" % sys.exc_info()[0])
        rollbar.report_exc_info()
        raise

@cli.command()
@click.argument('email')
@click.option('-p', '--password', default=None)
@click.option('-y', '--yes', is_flag=True)
def login(email, password, yes):
    try:
        while password == None or password == '':
            password = getpass.getpass()
        r = requests.get('http://localhost:4000/api/login', auth = (email, password))
        if r.status_code == 401:
            logging.error("Unauthorized")
        elif r.status_code != 200:
            raise Exception(r.text)
        else:
            key = json.loads(r.text)["key"]
            if yes or click.confirm('Would you like to save your api key to your ~/.netrc file?'):
                # TODO: support netrc files in locations other than ~/.netrc
                netrc_file = netrc.netrc()
                netrc_file.hosts['git.gigalixir.com'] = (email.encode('utf8'), None, key.encode('utf8'))
                netrc_file.hosts['localhost'] = (email.encode('utf8'), None, key.encode('utf8'))
                netrc_file.hosts['api.gigalixir.com'] = (email.encode('utf8'), None, key.encode('utf8'))
                file = os.path.join(os.environ['HOME'], ".netrc")
                with open(file, 'w') as fp:
                    fp.write(netrc_repr(netrc_file))
            else:
                logging.info('Your api key is %s' % key)
    except:
        click.echo("Unexpected error: %s" % sys.exc_info()[0])
        rollbar.report_exc_info()
        raise

@create.command()
@click.argument('unique_name')
def app(unique_name):
    try:
        # check for git folder
        with open(os.devnull, 'w') as FNULL:
            subprocess.check_call('git rev-parse --is-inside-git-dir'.split(), stdout=FNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        logging.error("You must call this from inside a git repository.")
        sys.exit(1)

    try:
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
    except:
        click.echo("Unexpected error: %s" % sys.exc_info()[0])
        rollbar.report_exc_info()
        raise

@create.command()
@click.argument('email')
@click.argument('card_number')
@click.argument('card_exp_month')
@click.argument('card_exp_year')
@click.argument('card_cvc')
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-y', '--accept_terms_of_service_and_privacy_policy', is_flag=True)
def account(email, card_number, card_exp_month, card_exp_year, card_cvc, password, accept_terms_of_service_and_privacy_policy):
    if not accept_terms_of_service_and_privacy_policy:
        logging.info("GIGALIXIR Terms of Service: FPO")
        logging.info("GIGALIXIR Privacy Policy: FPO")
        if not click.confirm('Do you accept the Terms of Service and Privacy Policy?'):
            logging.error("Sorry, you must accept the Terms of Service and Privacy Policy to continue.")
            sys.exit(1)
    try:
        token = stripe.Token.create(
            card={
                "number": card_number,
                "exp_month": card_exp_month,
                "exp_year": card_exp_year,
                "cvc": card_cvc,
            },
        )
        r = requests.post('http://localhost:4000/api/users', headers = {
            'Content-Type': 'application/json',
        }, json = {
            'email': email,
            'password': password,
            'stripe_token': token["id"],
        })
        if r.status_code != 200:
            raise Exception(r.text)
    except:
        click.echo("Unexpected error: %s" % sys.exc_info()[0])
        rollbar.report_exc_info()
        raise

@cli.command()
@click.argument('app_name')
@click.argument('ssh_ip')
@click.pass_context
def observer(ctx, app_name, ssh_ip):
    """
    launch remote observer to inspect your production nodes
    """
    try:
        click.echo("Fetching pod ip and cookie.")
        ERLANG_COOKIE = call(" ".join(["ssh", "root@%s" % ssh_ip, "--", "cat", "/observer/ERLANG_COOKIE"]))
        MY_POD_IP = call("ssh root@%s cat /observer/MY_POD_IP" % ssh_ip)
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
        rollbar.report_exc_info()
        raise

    try:
        click.echo("Setting up SSH tunnel for ports %s and %s" % (APP_PORT, EPMD_PORT))
        cmd = "".join(["ssh -L %s" % APP_PORT, ":localhost:", "%s -L %s" % (APP_PORT, EPMD_PORT), ":localhost:", "%s root@%s -f -N" % (EPMD_PORT, ssh_ip)])
        cast(cmd)
        click.echo("Routing %s to 127.0.0.1" % MY_POD_IP)
        ctx.obj['router'].route_to_localhost(MY_POD_IP)
        name = uuid.uuid4()
        # cmd = "iex --name %(name)s@%(MY_POD_IP)s --cookie %(ERLANG_COOKIE)s --hidden -e ':observer.start()'" % {"name": name, "MY_POD_IP": MY_POD_IP, "ERLANG_COOKIE": ERLANG_COOKIE}
        cmd = "erl -name %(name)s@%(MY_POD_IP)s -setcookie %(ERLANG_COOKIE)s -hidden -run observer" % {"name": name, "MY_POD_IP": MY_POD_IP, "ERLANG_COOKIE": ERLANG_COOKIE}
        click.echo("Running observer using: %s" % cmd)
        click.echo("In the 'Node' menu, click 'Connect Node'" )
        click.echo("Enter: %(app_name)s@%(MY_POD_IP)s" % {"app_name": app_name, "MY_POD_IP": MY_POD_IP})
        cast(cmd)
    except:
        click.echo("Unexpected error: %s" % sys.exc_info()[0])
        rollbar.report_exc_info()
        raise
    finally:
        clean_up(ctx.obj['router'], MY_POD_IP, EPMD_PORT, APP_PORT)

# Copied from https://github.com/enthought/Python-2.7.3/blob/master/Lib/netrc.py#L105
# but uses str() instead of repr(). If the .netrc file uses quotes, repr will treat the quotes
# as part of the value and wrap it in another quote resulting in double quotes. I need to dig
# into this deeper, but this works for now.
def netrc_repr(netrc):
    rep = ""
    for host in netrc.hosts.keys():
        attrs = netrc.hosts[host]
        rep = rep + "machine "+ host + "\n\tlogin " + str(attrs[0]) + "\n"
        if attrs[1]:
            rep = rep + "account " + str(attrs[1])
        rep = rep + "\tpassword " + str(attrs[2]) + "\n"
    for macro in netrc.macros.keys():
        rep = rep + "macdef " + macro + "\n"
        for line in netrc.macros[macro]:
            rep = rep + line
        rep = rep + "\n"
    return rep
