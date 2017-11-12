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

@click.group(context_settings=CONTEXT_SETTINGS)
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
    click.echo(ctx.parent.get_help(), color=ctx.color)

@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def status(ctx, app_name):
    """
    Current app status.
    """
    gigalixir_app.status(ctx.obj['host'], app_name)

@cli.command()
@click.argument('app_name')
@click.argument('database_id')
@click.option('-s', '--size', type=float, default=0.6, help='Size of the database can be 0.6, 1.7, 4, 8, 16, 32, 64, or 128.')
@click.pass_context
@report_errors
def scale_database(ctx, app_name, database_id, size):
    """
    Scale database.
    """
    gigalixir_database.scale(ctx.obj['host'], app_name, database_id, size)

@cli.command()
@click.argument('app_name')
@click.option('-r', '--replicas', type=int, help='Number of replicas to run.')
@click.option('-s', '--size', type=float, help='Size of each replica between 0.5 and 128 in increments of 0.1.')
@click.pass_context
@report_errors
def scale(ctx, app_name, replicas, size):
    """
    Scale app.
    """
    gigalixir_app.scale(ctx.obj['host'], app_name, replicas, size)

@cli.command()
@click.argument('app_name')
@click.option('-r', '--version', default=None, help='The version of the release to revert to. Use gigalixir get releases to find the version. If omitted, this defaults to the second most recent release.')
@click.pass_context
@report_errors
def rollback(ctx, app_name, version):
    """
    Rollback to a previous release. 
    """
    gigalixir_app.rollback(ctx.obj['host'], app_name, version)


@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def remote_console(ctx, app_name):
    """
    Drop into a remote console on a live production node.
    """
    gigalixir_app.ssh(ctx.obj['host'], app_name, 'remote_console')

@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def ssh(ctx, app_name):
    """
    Ssh into app. Be sure you added your ssh key using gigalixir create ssh_key.
    """
    gigalixir_app.ssh(ctx.obj['host'], app_name)

@cli.command()
@click.argument('app_name')
@click.argument('distillery_command', nargs=-1)
@click.pass_context
@report_errors
def distillery(ctx, app_name, distillery_command):
    """
    Runs a distillery command to run on the remote container e.g. ping, remote_console. Be sure you've added your ssh key.
    """
    gigalixir_app.ssh(ctx.obj['host'], app_name, *distillery_command)

@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def restart(ctx, app_name):
    """
    Restart app.
    """
    gigalixir_app.restart(ctx.obj['host'], app_name)


@cli.command()
@click.argument('app_name')
@click.argument('module')
@click.argument('function')
@click.pass_context
@report_errors
def run(ctx, app_name, module, function):
    """
    Run arbitrary function e.g. Elixir.Tasks.migrate/0. Runs as a job in a separate process.
    """
    gigalixir_app.run(ctx.obj['host'], app_name, module, function)

@cli.command()
@click.argument('app_name')
@click.option('-m', '--migration_app_name', default=None, help='For umbrella apps, specify which inner app to migrate.')
@click.pass_context
@report_errors
def migrate(ctx, app_name, migration_app_name):
    """
    Run Ecto Migrations on a production node.
    """
    gigalixir_app.migrate(ctx.obj['host'], app_name, migration_app_name)

# @update.command()
@cli.command()
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

@cli.command()
@click.pass_context
@report_errors
def upgrade(ctx):
    """
    Upgrade from free tier to standard tier.
    """
    if click.confirm('Are you sure you want to upgrade to the standard tier?'):
        gigalixir_user.upgrade(ctx.obj['host'])

# @reset.command()
@cli.command()
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
@cli.command()
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
@cli.command()
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
@click.argument('app_name')
@click.pass_context
@report_errors
def logs(ctx, app_name):
    """
    Stream logs from app.
    """
    gigalixir_app.logs(ctx.obj['host'], app_name)

# @get.command()
@cli.command()
@click.pass_context
@report_errors
def payment_method(ctx):
    """
    Get your payment method.
    """
    gigalixir_payment_method.get(ctx.obj['host'])

# @get.command()
@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def log_drains(ctx, app_name):
    """
    Get your log drains.
    """
    gigalixir_log_drain.get(ctx.obj['host'], app_name)


# @get.command()
@cli.command()
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
@click.argument('app_name')
@click.pass_context
@report_errors
def releases(ctx, app_name):
    """
    Get previous releases for app.
    """
    gigalixir_release.get(ctx.obj['host'], app_name)


# @get.command()
@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def permissions(ctx, app_name):
    """
    Get permissions for app.
    """
    gigalixir_permission.get(ctx.obj['host'], app_name)

# @create.command()
@cli.command()
@click.argument('app_name')
@click.argument('url')
@click.pass_context
@report_errors
def add_log_drain(ctx, app_name, url):
    """
    Add a drain to send your logs to.
    """
    gigalixir_log_drain.create(ctx.obj['host'], app_name, url)


# @create.command()
@cli.command()
@click.argument('ssh_key')
@click.pass_context
@report_errors
def add_ssh_key(ctx, ssh_key):
    """
    Add an ssh key.
    """
    gigalixir_ssh_key.create(ctx.obj['host'], ssh_key)

# @create.command()
@cli.command()
@click.argument('app_name')
@click.argument('fully_qualified_domain_name')
@click.pass_context
@report_errors
def add_domain(ctx, app_name, fully_qualified_domain_name):
    """
    Adds a custom domain name to your app. 
    """
    gigalixir_domain.create(ctx.obj['host'], app_name, fully_qualified_domain_name)

# @create.command()
@cli.command()
@click.argument('app_name')
@click.argument('key')
@click.argument('value')
@click.pass_context
@report_errors
def set_config(ctx, app_name, key, value):
    """
    Set an app configuration/environment variable.
    """
    gigalixir_config.create(ctx.obj['host'], app_name, key, value)

# @get.command()
@cli.command()
@click.option('-e', '--email', prompt=True)
@click.pass_context
@report_errors
def send_email_confirmation_token(ctx, email):
    """
    Regenerate a email confirmation token and send to email.
    """
    gigalixir_user.get_confirmation_token(ctx.obj['host'], email)

# @get.command()
@cli.command()
@click.option('-e', '--email', prompt=True)
@click.pass_context
@report_errors
def send_reset_password_token(ctx, email):
    """
    Send reset password token to email.
    """
    gigalixir_user.get_reset_password_token(ctx.obj['host'], email)

# @get.command()
@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def databases(ctx, app_name):
    """
    Get databases for your app.
    """
    gigalixir_database.get(ctx.obj['host'], app_name)

# @get.command()
@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def free_databases(ctx, app_name):
    """
    Get free databases for your app.
    """
    gigalixir_free_database.get(ctx.obj['host'], app_name)

# @get.command()
@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def domains(ctx, app_name):
    """
    Get custom domains for your app.
    """
    gigalixir_domain.get(ctx.obj['host'], app_name)

# @get.command()
@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def configs(ctx, app_name):
    """
    Get app configuration/environment variables.
    """
    gigalixir_config.get(ctx.obj['host'], app_name)

# @delete.command()
@cli.command()
@click.argument('app_name')
@click.argument('drain_id')
@click.pass_context
@report_errors
def delete_log_drain(ctx, app_name, drain_id):
    """
    Deletes a log drain. Find the drain_id from gigalixir log_drains.
    """
    gigalixir_log_drain.delete(ctx.obj['host'], app_name, drain_id)

# @delete.command()
@cli.command()
@click.argument('key_id')
@click.pass_context
@report_errors
def delete_ssh_key(ctx, key_id):
    """
    Deletes your ssh key. Find the key_id from gigalixir get_ssh_keys.
    """
    gigalixir_ssh_key.delete(ctx.obj['host'], key_id)

@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def delete_app(ctx, app_name):
    """
    Deletes an app. Can not be undone. 
    """
    logging.getLogger("gigalixir-cli").info("WARNING!! Deleting an app can not be undone and the name can not be reused.")
    if click.confirm('Do you want to delete your app?'):
        gigalixir_app.delete(ctx.obj['host'], app_name)

# @delete.command()
@cli.command()
@click.argument('app_name')
@click.argument('email')
@click.pass_context
@report_errors
def delete_permission(ctx, app_name, email):
    """
    Denies user access to app.
    """
    gigalixir_permission.delete(ctx.obj['host'], app_name, email)

# @delete.command()
@cli.command()
@click.argument('app_name')
@click.argument('database_id')
@click.pass_context
@report_errors
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
@cli.command()
@click.argument('app_name')
@click.argument('database_id')
@click.pass_context
@report_errors
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
@cli.command()
@click.argument('app_name')
@click.argument('fully_qualified_domain_name')
@click.pass_context
@report_errors
def delete_domain(ctx, app_name, fully_qualified_domain_name):
    """
    Delete custom domain from your app.
    """
    gigalixir_domain.delete(ctx.obj['host'], app_name, fully_qualified_domain_name)

# @delete.command()
@cli.command()
@click.argument('app_name')
@click.argument('key')
@click.pass_context
@report_errors
def delete_config(ctx, app_name, key):
    """
    Delete app configuration/environment variables.
    """
    gigalixir_config.delete(ctx.obj['host'], app_name, key)

# @create.command()
@cli.command()
@click.argument('unique_name')
@click.argument('email')
@click.pass_context
@report_errors
def add_permission(ctx, unique_name, email):
    """
    Grants a user permission to deploy an app.
    """
    gigalixir_permission.create(ctx.obj['host'], unique_name, email)


@cli.command()
@click.argument('app_name')
@click.option('-s', '--size', type=float, default=0.6, help='Size of the database can be 0.6, 1.7, 4, 8, 16, 32, 64, or 128.')
@click.pass_context
@report_errors
def create_database(ctx, app_name, size):
    """
    Create a new database for app.
    """
    gigalixir_database.create(ctx.obj['host'], app_name, size)

@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def create_free_database(ctx, app_name):
    """
    Create a new free database for app.
    """
    gigalixir_free_database.create(ctx.obj['host'], app_name)

# @create.command()
@cli.command()
@click.argument('app_name')
@click.pass_context
@report_errors
def set_git_remote(ctx, app_name):
    """
    Set the gigalixir git remote.
    """
    gigalixir_app.set_git_remote(ctx.obj['host'], app_name)

# @create.command()
@cli.command()
@click.option('-n', '--name')
@click.pass_context
@report_errors
def create(ctx, name):
    """
    Create a new app.
    """
    gigalixir_app.create(ctx.obj['host'], name)

@cli.command()
@click.pass_context
@report_errors
def invoices(ctx):
    """
    List all previous invoices.
    """
    gigalixir_invoice.get(ctx.obj['host'])

@cli.command()
@click.pass_context
@report_errors
def current_period_usage(ctx):
    """
    See how much usage you've accumulated so far this month.
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

@cli.command()
@click.argument('app_name')
@click.option('-c', '--cookie')
@click.pass_context
@report_errors
def observer(ctx, app_name, cookie):
    """
    Launch remote production observer.
    """
    gigalixir_observer.observer(ctx, app_name, cookie)

