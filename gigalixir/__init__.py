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
from . import payment_method as gigalixir_payment_method
from . import domain as gigalixir_domain
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

@click.group()
@click.option('--host', envvar='GIGALIXIR_HOST', default="https://api.gigalixir.com")
@click.pass_context
def cli(ctx, host):
    ctx.obj = {}
    logging.basicConfig(format='%(message)s', level = logging.INFO)
    ROLLBAR_POST_CLIENT_ITEM = "6fb30e5647474decb3fc8f3175e1dfca"
    rollbar.init(ROLLBAR_POST_CLIENT_ITEM, 'production', enabled=False)

    stripe.api_key = 'pk_test_6tMDkFKTz4N0wIFQZHuzOUyW'
    # stripe.api_key = 'pk_live_45dmSl66k4xLy4X4yfF3RVpd'

    ctx.obj['host'] = host

    PLATFORM = call("uname -s").lower() # linux or darwin
    if PLATFORM == "linux":
        ctx.obj['router'] = LinuxRouter()
    elif PLATFORM == "darwin":
        ctx.obj['router'] = DarwinRouter()
    else:
        raise Exception("Unknown platform: %s" % PLATFORM)

@cli.group()
def get():
    """
    Get users, apps, etc.
    """
    pass

@cli.group()
def create():
    """
    Create users, apps, etc.
    """
    pass

@cli.group()
def update():
    """
    Update users, apps, etc.
    """
    pass

@cli.group()
def delete():
    """
    Delete configs, etc
    """
    pass

@cli.command()
@click.argument('app_name')
@click.option('-r', '--replicas', type=int, default=None, help='Number of replicas to run.')
@click.option('-s', '--size', type=float, default=None, help='Size of each replica between 0.5 and 128 in increments of 0.1.')
@click.pass_context
def scale(ctx, app_name, replicas, size):
    """
    Scale app.
    """
    try:
        gigalixir_app.scale(ctx.obj['host'], app_name, replicas, size)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@cli.command()
@click.argument('app_name')
@click.option('-r', '--rollback_id', default=None, help='The rollback id of the release to revert to. Use gigalixir get releases to find the rollback_id. If omitted, this defaults to the second most recent release.')
@click.pass_context
def rollback(ctx, app_name, rollback_id):
    """
    Rollback to a previous release. 
    """
    try:
        gigalixir_app.rollback(ctx.obj['host'], app_name, rollback_id)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@cli.command()
@click.argument('app_name')
@click.option('-c', '--distillery_command', default="", help='The distillery command to run on the remote container e.g. ping, remote_console.')
@click.pass_context
def ssh(ctx, app_name, distillery_command):
    """
    Ssh into app. Be sure you added your ssh key using gigalixir create ssh_key.
    """
    try:
        gigalixir_app.ssh(ctx.obj['host'], app_name, distillery_command)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@cli.command()
@click.argument('app_name')
@click.pass_context
def restart(ctx, app_name):
    """
    Restart app.
    """
    try:
        gigalixir_app.restart(ctx.obj['host'], app_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@cli.command()
@click.argument('app_name')
@click.argument('module')
@click.argument('function')
@click.pass_context
def run(ctx, app_name, module, function):
    """
    Run arbitrary function e.g. Elixir.Tasks.migrate/0.
    """
    try:
        gigalixir_app.run(ctx.obj['host'], app_name, module, function)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@update.command()
@click.argument('stripe_token')
@click.pass_context
def payment_method(ctx, stripe_token):
    """
    Update your payment method.
    """
    try:
        gigalixir_payment_method.update(ctx.obj['host'], stripe_token)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@update.command()
@click.argument('email')
@click.option('-p', '--current_password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-n', '--new_password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.pass_context
def user(ctx, email, current_password, new_password):
    """
    Edit user. Currently only password is editable.
    """
    try:
        gigalixir_user.change_password(ctx.obj['host'], email, current_password, new_password)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@update.command()
@click.argument('email')
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
def api_key(ctx, email, password, yes):
    """
    Regenerate a new api key to replace the old one.
    """
    try:
        gigalixir_api_key.regenerate(ctx.obj['host'], email, password, yes)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@cli.command()
@click.option('-e', '--email', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
def login(ctx, email, password, yes):
    """
    Login and receive an api key.
    """
    try:
        gigalixir_user.login(ctx.obj['host'], email, password, yes)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@get.command()
@click.argument('app_name')
@click.pass_context
def logs(ctx, app_name):
    """
    Stream logs from app.
    """
    try:
        gigalixir_app.logs(ctx.obj['host'], app_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@get.command()
@click.pass_context
def payment_method(ctx):
    """
    Get your payment method.
    """
    try:
        gigalixir_payment_method.get(ctx.obj['host'])
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@get.command()
@click.pass_context
def ssh_keys(ctx):
    """
    Get your ssh keys.
    """
    try:
        gigalixir_ssh_key.get(ctx.obj['host'])
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@get.command()
@click.pass_context
def apps(ctx):
    """
    Get apps.
    """
    try:
        gigalixir_app.get(ctx.obj['host'])
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@get.command()
@click.argument('app_name')
@click.pass_context
def releases(ctx, app_name):
    """
    Get previous releases for app.
    """
    try:
        gigalixir_release.get(ctx.obj['host'], app_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@get.command()
@click.argument('app_name')
@click.pass_context
def permissions(ctx, app_name):
    """
    Get permissions for app.
    """
    try:
        gigalixir_permission.get(ctx.obj['host'], app_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@create.command()
@click.argument('ssh_key')
@click.pass_context
def ssh_key(ctx, ssh_key):
    """
    Create ssh key.
    """
    try:
        gigalixir_ssh_key.create(ctx.obj['host'], ssh_key)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@create.command()
@click.argument('app_name')
@click.argument('fully_qualified_domain_name')
@click.pass_context
def domain(ctx, app_name, fully_qualified_domain_name):
    """
    Adds a custom domain name to your app. 
    """
    try:
        gigalixir_domain.create(ctx.obj['host'], app_name, fully_qualified_domain_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@create.command()
@click.argument('app_name')
@click.argument('key')
@click.argument('value')
@click.pass_context
def config(ctx, app_name, key, value):
    """
    Create app configuration/environment variable.
    """
    try:
        gigalixir_config.create(ctx.obj['host'], app_name, key, value)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@get.command()
@click.argument('app_name')
@click.pass_context
def domains(ctx, app_name):
    """
    Get custom domains for your app.
    """
    try:
        gigalixir_domain.get(ctx.obj['host'], app_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@get.command()
@click.argument('app_name')
@click.pass_context
def configs(ctx, app_name):
    """
    Get app configuration/environment variables.
    """
    try:
        gigalixir_config.get(ctx.obj['host'], app_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@delete.command()
@click.argument('key_id')
@click.pass_context
def ssh_key(ctx, key_id):
    """
    Deletes your ssh key. Find the key_id from gigalixir get ssh_keys.
    """
    try:
        gigalixir_ssh_key.delete(ctx.obj['host'], key_id)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@delete.command()
@click.argument('app_name')
@click.argument('email')
@click.pass_context
def permission(ctx, app_name, email):
    """
    Denies user access to app.
    """
    try:
        gigalixir_permission.delete(ctx.obj['host'], app_name, email)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@delete.command()
@click.argument('app_name')
@click.argument('fully_qualified_domain_name')
@click.pass_context
def domain(ctx, app_name, fully_qualified_domain_name):
    """
    Delete custom domain from your app.
    """
    try:
        gigalixir_domain.delete(ctx.obj['host'], app_name, fully_qualified_domain_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@delete.command()
@click.argument('app_name')
@click.argument('key')
@click.pass_context
def config(ctx, app_name, key):
    """
    Delete app configuration/environment variables.
    """
    try:
        gigalixir_config.delete(ctx.obj['host'], app_name, key)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@create.command()
@click.argument('unique_name')
@click.argument('email')
@click.pass_context
def permission(ctx, unique_name, email):
    """
    Grants another user permission to collaborate on an app.
    """
    try:
        gigalixir_permission.create(ctx.obj['host'], unique_name, email)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@create.command()
@click.argument('unique_name')
@click.pass_context
def app(ctx, unique_name):
    """
    Create a new app.
    """
    try:
        gigalixir_app.create(ctx.obj['host'], unique_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@create.command()
@click.option('--email', prompt=True)
@click.option('--card_number', prompt=True)
@click.option('--card_exp_month', prompt=True)
@click.option('--card_exp_year', prompt=True)
@click.option('--card_cvc', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-y', '--accept_terms_of_service_and_privacy_policy', is_flag=True)
@click.pass_context
def user(ctx, email, card_number, card_exp_month, card_exp_year, card_cvc, password, accept_terms_of_service_and_privacy_policy):
    """
    Create a new user.
    """
    try:
        gigalixir_user.create(ctx.obj['host'], email, card_number, card_exp_month, card_exp_year, card_cvc, password, accept_terms_of_service_and_privacy_policy)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@cli.command()
@click.argument('app_name')
@click.argument('ssh_ip')
@click.pass_context
def observer(ctx, app_name, ssh_ip):
    """
    Launch remote production observer.
    """
    gigalixir_observer.observer(ctx, app_name, ssh_ip)

