from .shell import cast, call
from .routers.linux import LinuxRouter
from .routers.darwin import DarwinRouter
from . import observer as gigalixir_observer
from . import user as gigalixir_user
from . import app as gigalixir_app
from . import config as gigalixir_config
from . import permission as gigalixir_permission
from . import release as gigalixir_release
from . import api_key as gigalixir_api_key
from . import ssh_key as gigalixir_ssh_key
from . import log_drain as gigalixir_log_drain
from . import payment_method as gigalixir_payment_method
from . import domain as gigalixir_domain
from . import invoice as gigalixir_invoice
from . import usage as gigalixir_usage
from . import database as gigalixir_database
from . import free_database as gigalixir_free_database
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
from functools import wraps
import pkg_resources

def detect_app_name(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        app_name = kwds['app_name']
        if app_name is None:
            app_name = detect_app()
        kwds['app_name'] = app_name
        f(*args, **kwds)
    return wrapper

def report_errors(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        try:
            f(*args, **kwds)
        except:
            logging.getLogger("gigalixir-cli").error(sys.exc_info()[1])
            rollbar.report_exc_info()
            sys.exit(1)
    return wrapper

# TODO: remove localhost from .netrc file

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        aliases = {
            "configs": "config",
            "set_config": "deprecated:set_config",
            "databases": "pg",
            "scale_database": "pg:scale",
            "delete_database": "pg:destroy",
            "status": "ps",
            "scale": "ps:scale",
            "rollback": "releases:rollback",
            "remote_console": "ps:remote_console",
            "ssh": "ps:ssh",
            "migrate": "ps:migrate",
            "set_payment_method": "account:payment_method:set",
            "payment_method": "account:payment_method",
            "set_password": "account:password:set",
            "change_password": "account:password:change",
            "reset_api_key": "account:api_key:reset",
            "upgrade": "account:upgrade",
            "log_drains": "drains",
            "delete_log_drain": "drains:remove",
            "ssh_keys": "account:ssh_keys",
            "add_log_drain": "drains:add",
            "add_ssh_key": "account:ssh_keys:add",
            "delete_ssh_key": "account:ssh_keys:remove",
            "add_domain": "domains:add",
            "send_email_confirmation_token": "account:confirmation:resend",
            "send_reset_password_token": "account:password:reset",
            "delete_app": "apps:destroy",
            "delete_permission": "access:remove",
            "permissions": "access",
            "delete_free_database": "deprecated:delete_free_database",
            "free_databases": "deprecated:free_databases",
            "create_free_database": "deprecated:create_free_database",
            "delete_domain": "domains:remove",
            "delete_config": "config:unset",
            "add_permission": "access:add",
            "create_database": "pg:create",
            "set_git_remote": "git:remote",
            "invoices": "account:invoices",
            "current_period_usage": "account:usage",
            "observer": "ps:observer",

            # permanent
            "create": "apps:create",
            "restart": "ps:restart",
        }
        if cmd_name not in aliases:
            return None
        else:
            return click.Group.get_command(self, ctx, aliases[cmd_name])

def detect_app():
    try:
        # check for git folder
        with open(os.devnull, 'w') as FNULL:
            subprocess.check_call('git rev-parse --is-inside-git-dir'.split(), stdout=FNULL, stderr=subprocess.STDOUT)
        remote = call("git remote -v")
        # matches first instance of
        # git.gigalixir.com/foo.git
        # git.gigalixir.com/foo.git/
        # git.gigalixir.com/foo
        repo_name = re.search('git.gigalixir.com/(.*) ', remote).group(1)
        # strip trailing .git stuff if it is there
        git_pos = repo_name.find(".git")
        if git_pos >= 0:
            repo_name = repo_name[:git_pos]
        return repo_name
    except (AttributeError, subprocess.CalledProcessError):
        raise Exception("Could not detect app name. Try passing the app name explicitly with the `-a` flag.")

@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.option('--env', envvar='GIGALIXIR_ENV', default='prod', help="GIGALIXIR environment [prod, dev].")
@click.pass_context
def cli(ctx, env):
    ctx.obj = {}
    logging.basicConfig(format='%(message)s')
    logging.getLogger("gigalixir-cli").setLevel(logging.INFO)
    ROLLBAR_POST_CLIENT_ITEM = "40403cdd48904a12b6d8d27050b12343"

    if env == "prod":
        stripe.api_key = 'pk_live_45dmSl66k4xLy4X4yfF3RVpd'
        rollbar.init(ROLLBAR_POST_CLIENT_ITEM, 'production', enabled=True)
        host = "https://api.gigalixir.com"
    elif env == "dev":
        stripe.api_key = 'pk_test_6tMDkFKTz4N0wIFQZHuzOUyW'
        rollbar.init(ROLLBAR_POST_CLIENT_ITEM, 'development', enabled=False)
        host = "http://localhost:4000"
    else:
        raise Exception("Invalid GIGALIXIR_ENV")

    ctx.obj['host'] = host

    PLATFORM = call("uname -s").lower() # linux or darwin
    if PLATFORM == "linux":
        ctx.obj['router'] = LinuxRouter()
    elif PLATFORM == "darwin":
        ctx.obj['router'] = DarwinRouter()
    else:
        raise Exception("Unknown platform: %s" % PLATFORM)

@cli.command()
@click.pass_context
@report_errors
def help(ctx):
    """
    Show commands and descriptions.
    """
    click.echo(ctx.parent.get_help(), color=ctx.color)

@cli.command(name='ps')
@click.option('-a', '--app_name')
@click.pass_context
@report_errors
@detect_app_name
def status(ctx, app_name):
    """
    Current app status.
    """
    gigalixir_app.status(ctx.obj['host'], app_name)

@cli.command(name='pg:scale')
@click.option('-a', '--app_name')
@click.argument('database_id')
@click.option('-s', '--size', type=float, default=0.6, help='Size of the database can be 0.6, 1.7, 4, 8, 16, 32, 64, or 128.')
@click.pass_context
@report_errors
@detect_app_name
def scale_database(ctx, app_name, database_id, size):
    """
    Scale database.
    """
    gigalixir_database.scale(ctx.obj['host'], app_name, database_id, size)

@cli.command(name='ps:scale')
@click.option('-a', '--app_name')
@click.option('-r', '--replicas', type=int, help='Number of replicas to run.')
@click.option('-s', '--size', type=float, help='Size of each replica between 0.5 and 128 in increments of 0.1.')
@click.pass_context
@report_errors
@detect_app_name
def scale(ctx, app_name, replicas, size):
    """
    Scale app.
    """
    gigalixir_app.scale(ctx.obj['host'], app_name, replicas, size)

@cli.command(name='releases:rollback')
@click.option('-a', '--app_name')
@click.option('-r', '--version', default=None, help='The version of the release to revert to. Use gigalixir get releases to find the version. If omitted, this defaults to the second most recent release.')
@click.pass_context
@report_errors
@detect_app_name
def rollback(ctx, app_name, version):
    """
    Rollback to a previous release. 
    """
    gigalixir_app.rollback(ctx.obj['host'], app_name, version)


@cli.command(name='ps:remote_console')
@click.option('-a', '--app_name')
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.pass_context
@report_errors
@detect_app_name
def remote_console(ctx, app_name, ssh_opts):
    """
    Drop into a remote console on a live production node.
    """
    gigalixir_app.remote_console(ctx.obj['host'], app_name, ssh_opts)

@cli.command(name='ps:run')
@click.option('-a', '--app_name')
@click.argument('command', nargs=-1)
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.pass_context
@report_errors
@detect_app_name
def ps_run(ctx, app_name, ssh_opts, command):
    """
    Run a shell command on your running container.
    """
    gigalixir_app.ps_run(ctx.obj['host'], app_name, ssh_opts, *command)

@cli.command(name='ps:ssh')
@click.option('-a', '--app_name')
@click.argument('command', nargs=-1)
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.pass_context
@report_errors
@detect_app_name
def ssh(ctx, app_name, ssh_opts, command):
    """
    Ssh into app. Be sure you added your ssh key using gigalixir create ssh_key. Configs are not loaded automatically.
    """
    gigalixir_app.ssh(ctx.obj['host'], app_name, ssh_opts, *command)

@cli.command(name='ps:distillery')
@click.option('-a', '--app_name')
@click.argument('distillery_command', nargs=-1)
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.pass_context
@report_errors
@detect_app_name
def distillery(ctx, app_name, ssh_opts, distillery_command):
    """
    Runs a distillery command to run on the remote container e.g. ping, remote_console. Be sure you've added your ssh key.
    """
    gigalixir_app.distillery_command(ctx.obj['host'], app_name, ssh_opts, *distillery_command)

@cli.command(name='ps:restart')
@click.option('-a', '--app_name')
@click.pass_context
@report_errors
@detect_app_name
def restart(ctx, app_name):
    """
    Restart app.
    """
    gigalixir_app.restart(ctx.obj['host'], app_name)


# gigalixir run mix ecto.migrate
@cli.command()
@click.option('-a', '--app_name')
@click.argument('command', nargs=-1)
@click.pass_context
@report_errors
@detect_app_name
def run(ctx, app_name, command):
    """
    Run shell command as a job in a separate process. Useful for migrating databases before the app is running.
    """
    gigalixir_app.run(ctx.obj['host'], app_name, command)

@cli.command(name='ps:migrate')
@click.option('-a', '--app_name')
@click.option('-m', '--migration_app_name', default=None, help='For umbrella apps, specify which inner app to migrate.')
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.pass_context
@report_errors
@detect_app_name
def ps_migrate(ctx, app_name, migration_app_name, ssh_opts):
    """
    Run Ecto Migrations on a production node.
    """
    gigalixir_app.migrate(ctx.obj['host'], app_name, migration_app_name, ssh_opts)

# @update.command()
@cli.command(name='account:payment_method:set')
@click.option('--card_number', prompt=True)
@click.option('--card_exp_month', prompt=True)
@click.option('--card_exp_year', prompt=True)
@click.option('--card_cvc', prompt=True)
@click.pass_context
@report_errors
def set_payment_method(ctx, card_number, card_exp_month, card_exp_year, card_cvc):
    """
    Set your payment method.
    """
    gigalixir_payment_method.update(ctx.obj['host'], card_number, card_exp_month, card_exp_year, card_cvc)

@cli.command(name='account:upgrade')
@click.pass_context
@report_errors
def upgrade(ctx):
    """
    Upgrade from free tier to standard tier.
    """
    if click.confirm('Are you sure you want to upgrade to the standard tier?'):
        gigalixir_user.upgrade(ctx.obj['host'])

# @reset.command()
@cli.command(name='account:password:set')
@click.option('-t', '--token', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.pass_context
@report_errors
def set_password(ctx, token, password):
    """
    Set password using reset password token.
    """
    gigalixir_user.reset_password(ctx.obj['host'], token, password)

# @update.command()
@cli.command(name='account:password:change')
@click.option('-e', '--email', prompt=True)
@click.option('-p', '--current_password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-n', '--new_password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.pass_context
@report_errors
def change_password(ctx, email, current_password, new_password):
    """
    Change password.
    """
    gigalixir_user.change_password(ctx.obj['host'], email, current_password, new_password)

@cli.command()
@click.pass_context
@report_errors
def account(ctx):
    """
    Account information.
    """
    gigalixir_user.account(ctx.obj['host'])

# @update.command()
@cli.command(name='account:api_key:reset')
@click.option('-e', '--email', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
def reset_api_key(ctx, email, password, yes):
    """
    Regenerate a replacement api key. 
    """
    gigalixir_api_key.regenerate(ctx.obj['host'], email, password, yes)


@cli.command()
@click.pass_context
@report_errors
def logout(ctx):
    """
    Logout
    """
    gigalixir_user.logout()

@cli.command()
@click.option('-e', '--email', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
def login(ctx, email, password, yes):
    """
    Login and receive an api key.
    """
    gigalixir_user.login(ctx.obj['host'], email, password, yes)

# @get.command()
@cli.command()
@click.option('-a', '--app_name')
@click.option('-n', '--num')
@click.option('-t', '--no_tail', is_flag=True)
@click.pass_context
@report_errors
@detect_app_name
def logs(ctx, app_name, num, no_tail):
    """
    Stream logs from app.
    """
    gigalixir_app.logs(ctx.obj['host'], app_name, num, no_tail)

# @get.command()
@cli.command(name='account:payment_method')
@click.pass_context
@report_errors
def payment_method(ctx):
    """
    Get your payment method.
    """
    gigalixir_payment_method.get(ctx.obj['host'])

# @get.command()
@cli.command(name='drains')
@click.option('-a', '--app_name')
@click.pass_context
@report_errors
@detect_app_name
def log_drains(ctx, app_name):
    """
    Get your log drains.
    """
    gigalixir_log_drain.get(ctx.obj['host'], app_name)


# @get.command()
@cli.command(name='account:ssh_keys')
@click.pass_context
@report_errors
def ssh_keys(ctx):
    """
    Get your ssh keys.
    """
    gigalixir_ssh_key.get(ctx.obj['host'])

# @get.command()
@cli.command()
@click.pass_context
@report_errors
def apps(ctx):
    """
    Get apps.
    """
    gigalixir_app.get(ctx.obj['host'])

# @get.command()
@cli.command()
@click.option('-a', '--app_name')
@click.pass_context
@report_errors
@detect_app_name
def releases(ctx, app_name):
    """
    Get previous releases for app.
    """
    gigalixir_release.get(ctx.obj['host'], app_name)


# @get.command()
@cli.command(name='access')
@click.option('-a', '--app_name')
@click.pass_context
@report_errors
@detect_app_name
def permissions(ctx, app_name):
    """
    Get permissions for app.
    """
    gigalixir_permission.get(ctx.obj['host'], app_name)

# @create.command()
@cli.command(name='drains:add')
@click.option('-a', '--app_name')
@click.argument('url')
@click.pass_context
@report_errors
@detect_app_name
def add_log_drain(ctx, app_name, url):
    """
    Add a drain to send your logs to.
    """
    gigalixir_log_drain.create(ctx.obj['host'], app_name, url)


# @create.command()
@cli.command(name='account:ssh_keys:add')
@click.argument('ssh_key')
@click.pass_context
@report_errors
def add_ssh_key(ctx, ssh_key):
    """
    Add an ssh key. Make sure you use the actual key and not the filename as the argument. For example,
    don't use ~/.ssh/id_rsa.pub, use the contents of that file.
    """
    gigalixir_ssh_key.create(ctx.obj['host'], ssh_key)

# @create.command()
@cli.command(name='domains:add')
@click.option('-a', '--app_name')
@click.argument('fully_qualified_domain_name')
@click.pass_context
@report_errors
@detect_app_name
def add_domain(ctx, app_name, fully_qualified_domain_name):
    """
    Adds a custom domain name to your app. 
    """
    gigalixir_domain.create(ctx.obj['host'], app_name, fully_qualified_domain_name)

# @create.command()
@cli.command(name='deprecated:set_config')
@click.option('-a', '--app_name')
@click.argument('key')
@click.argument('value')
@click.pass_context
@report_errors
@detect_app_name
def set_config(ctx, app_name, key, value):
    """
    Set an app configuration/environment variable.
    """
    gigalixir_config.create(ctx.obj['host'], app_name, key, value)

@cli.command(name="config:set")
@click.option('-a', '--app_name')
@click.argument('assignments', nargs=-1)
@click.pass_context
@report_errors
@detect_app_name
def config_set(ctx, app_name, assignments):
    """
    Set configuration variables.
    """
    colored_keys = []
    configs = {}
    for assignment in assignments:
        key, value = assignment.split('=', 1)
        configs[key] = value
        colored_key = click.style(key, fg='green')
        colored_keys.append(colored_key)
        click.echo("%s: %s" % (colored_key, value))
    colored_app_name = click.style(app_name, fg='blue')
    click.echo("Setting %s and restarting %s" % (', '.join(colored_keys), colored_app_name))
    gigalixir_config.create_multiple(ctx.obj['host'], app_name, configs)

# @get.command()
@cli.command(name='account:confirmation:resend')
@click.option('-e', '--email', prompt=True)
@click.pass_context
@report_errors
def send_email_confirmation_token(ctx, email):
    """
    Regenerate a email confirmation token and send to email.
    """
    gigalixir_user.get_confirmation_token(ctx.obj['host'], email)

# @get.command()
@cli.command(name='account:password:reset')
@click.option('-e', '--email', prompt=True)
@click.pass_context
@report_errors
def send_reset_password_token(ctx, email):
    """
    Send reset password token to email.
    """
    gigalixir_user.get_reset_password_token(ctx.obj['host'], email)

# @get.command()
@cli.command(name='pg')
@click.option('-a', '--app_name')
@click.pass_context
@report_errors
@detect_app_name
def databases(ctx, app_name):
    """
    Get databases for your app.
    """
    gigalixir_database.get(ctx.obj['host'], app_name)

# @get.command()
# deprecated. pg/databases above lists free and standard.
@cli.command(name='deprecated:free_databases')
@click.option('-a', '--app_name')
@click.pass_context
@report_errors
@detect_app_name
def free_databases(ctx, app_name):
    """
    Get free databases for your app.
    """
    gigalixir_free_database.get(ctx.obj['host'], app_name)

# @get.command()
@cli.command()
@click.option('-a', '--app_name')
@click.pass_context
@report_errors
@detect_app_name
def domains(ctx, app_name):
    """
    Get custom domains for your app.
    """
    gigalixir_domain.get(ctx.obj['host'], app_name)

# @get.command()
@cli.command()
@click.option('-a', '--app_name')
@click.pass_context
@report_errors
@detect_app_name
def config(ctx, app_name):
    """
    Get app configuration/environment variables.
    """
    gigalixir_config.get(ctx.obj['host'], app_name)

# @delete.command()
@cli.command(name='drains:remove')
@click.option('-a', '--app_name')
@click.argument('drain_id')
@click.pass_context
@report_errors
@detect_app_name
def delete_log_drain(ctx, app_name, drain_id):
    """
    Deletes a log drain. Find the drain_id from gigalixir log_drains.
    """
    gigalixir_log_drain.delete(ctx.obj['host'], app_name, drain_id)

# @delete.command()
@cli.command(name='account:ssh_keys:remove')
@click.argument('key_id')
@click.pass_context
@report_errors
def delete_ssh_key(ctx, key_id):
    """
    Deletes your ssh key. Find the key_id from gigalixir get_ssh_keys.
    """
    gigalixir_ssh_key.delete(ctx.obj['host'], key_id)

@cli.command(name='apps:destroy')
@click.option('-a', '--app_name')
@click.pass_context
@report_errors
@detect_app_name
def delete_app(ctx, app_name):
    """
    Deletes an app. Can not be undone. 
    """
    logging.getLogger("gigalixir-cli").info("WARNING!! Deleting an app can not be undone and the name can not be reused.")
    if click.confirm('Do you want to delete your app?'):
        gigalixir_app.delete(ctx.obj['host'], app_name)

# @delete.command()
@cli.command(name='access:remove')
@click.option('-a', '--app_name')
@click.argument('email')
@click.pass_context
@report_errors
@detect_app_name
def delete_permission(ctx, app_name, email):
    """
    Denies user access to app.
    """
    gigalixir_permission.delete(ctx.obj['host'], app_name, email)

# @delete.command()
@cli.command(name='pg:destroy')
@click.option('-a', '--app_name')
@click.argument('database_id')
@click.pass_context
@report_errors
@detect_app_name
def delete_database(ctx, app_name, database_id):
    """
    Delete database.
    """
    logging.getLogger("gigalixir-cli").info("WARNING!! Deleting your database will all your data and backups.")
    logging.getLogger("gigalixir-cli").info("WARNING!! This can not be undone.")
    logging.getLogger("gigalixir-cli").info("WARNING!! Please make sure you backup your data first.")
    if click.confirm('Do you want to delete your database and all backups?'):
        gigalixir_database.delete(ctx.obj['host'], app_name, database_id)

# @delete.command()
# is this command still needed? i think delete_database/pg:destroy above can delete free databases?
@cli.command(name='deprecated:delete_free_database')
@click.option('-a', '--app_name')
@click.argument('database_id')
@click.pass_context
@report_errors
@detect_app_name
def delete_free_database(ctx, app_name, database_id):
    """
    Delete free database.
    """
    logging.getLogger("gigalixir-cli").info("WARNING!! Deleting your database will destroy all your data.")
    logging.getLogger("gigalixir-cli").info("WARNING!! This can not be undone.")
    logging.getLogger("gigalixir-cli").info("WARNING!! Please make sure you backup your data first.")
    if click.confirm('Do you want to delete your database?'):
        gigalixir_free_database.delete(ctx.obj['host'], app_name, database_id)

# @delete.command()
@cli.command(name='domains:remove')
@click.option('-a', '--app_name')
@click.argument('fully_qualified_domain_name')
@click.pass_context
@report_errors
@detect_app_name
def delete_domain(ctx, app_name, fully_qualified_domain_name):
    """
    Delete custom domain from your app.
    """
    gigalixir_domain.delete(ctx.obj['host'], app_name, fully_qualified_domain_name)

# @delete.command()
@cli.command(name='config:unset')
@click.option('-a', '--app_name')
@click.argument('key')
@click.pass_context
@report_errors
@detect_app_name
def delete_config(ctx, app_name, key):
    """
    Delete app configuration/environment variables.
    """
    gigalixir_config.delete(ctx.obj['host'], app_name, key)

# @create.command()
@cli.command(name='access:add')
@click.option('-a', '--app_name')
@click.argument('email')
@click.pass_context
@report_errors
@detect_app_name
def add_permission(ctx, app_name, email):
    """
    Grants a user permission to deploy an app.
    """
    gigalixir_permission.create(ctx.obj['host'], app_name, email)


@cli.command(name='pg:create')
@click.option('-a', '--app_name')
@click.option('-s', '--size', type=float, default=0.6, help='Size of the database can be 0.6, 1.7, 4, 8, 16, 32, 64, or 128.')
@click.option('-f', '--free', is_flag=True)
@click.pass_context
@report_errors
@detect_app_name
def create_database(ctx, app_name, size, free):
    """
    Create a new database for app.
    """
    if free:
        gigalixir_free_database.create(ctx.obj['host'], app_name)
    else:
        gigalixir_database.create(ctx.obj['host'], app_name, size)

@cli.command(name='deprecated:create_free_database')
@click.option('-a', '--app_name')
@click.pass_context
@report_errors
@detect_app_name
def create_free_database(ctx, app_name):
    """
    Create a new free database for app.
    """
    gigalixir_free_database.create(ctx.obj['host'], app_name)

# @create.command()
@cli.command(name='git:remote')
@click.argument('app_name')
@click.pass_context
@report_errors
def set_git_remote(ctx, app_name):
    """
    Set the gigalixir git remote.
    """
    gigalixir_app.set_git_remote(ctx.obj['host'], app_name)

# @create.command()
@cli.command(name='apps:create')
@click.option('-n', '--name')
@click.option('-c', '--cloud')
@click.option('-r', '--region')
@click.pass_context
@report_errors
def create(ctx, name, cloud, region):
    """
    Create a new app.
    """
    gigalixir_app.create(ctx.obj['host'], name, cloud, region)

@cli.command(name='account:invoices')
@click.pass_context
@report_errors
def invoices(ctx):
    """
    List all previous invoices.
    """
    gigalixir_invoice.get(ctx.obj['host'])

@cli.command(name='account:usage')
@click.pass_context
@report_errors
def current_period_usage(ctx):
    """
    See the usage so far this month.
    """
    gigalixir_usage.get(ctx.obj['host'])

# @create.command()
@cli.command()
@click.option('--email')
@click.option('-p', '--password')
@click.option('-y', '--accept_terms_of_service_and_privacy_policy', is_flag=True)
@click.pass_context
@report_errors
def signup(ctx, email, password, accept_terms_of_service_and_privacy_policy):
    """
    Sign up for a new account.
    """
    if not accept_terms_of_service_and_privacy_policy:
        logging.getLogger("gigalixir-cli").info("GIGALIXIR Terms of Service: https://www.gigalixir.com/terms")
        logging.getLogger("gigalixir-cli").info("GIGALIXIR Privacy Policy: https://www.gigalixir.com/privacy")
        if not click.confirm('Do you accept the Terms of Service and Privacy Policy?'):
            raise Exception("You must accept the Terms of Service and Privacy Policy to continue.")

    if email == None:
        email = click.prompt('Email')
    gigalixir_user.validate_email(ctx.obj['host'], email)

    if password == None:
        password = click.prompt('Password', hide_input=True)
    gigalixir_user.validate_password(ctx.obj['host'], password)

    gigalixir_user.create(ctx.obj['host'], email, password, accept_terms_of_service_and_privacy_policy)

@cli.command(name='ps:observer')
@click.option('-a', '--app_name')
@click.option('-c', '--cookie')
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.pass_context
@report_errors
@detect_app_name
def observer(ctx, app_name, cookie, ssh_opts):
    """
    Launch remote production observer.
    """
    gigalixir_observer.observer(ctx, app_name, cookie, ssh_opts)

@cli.command()
@click.pass_context
@report_errors
def version(ctx):
    """
    Show the CLI version.
    """
    click.echo(pkg_resources.get_distribution("gigalixir").version)

