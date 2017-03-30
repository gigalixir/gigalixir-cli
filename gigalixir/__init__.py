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
@click.pass_context
def cli(ctx):
    ctx.obj = {}
    logging.basicConfig(format='%(message)s', level = logging.INFO)
    ROLLBAR_POST_CLIENT_ITEM = "6fb30e5647474decb3fc8f3175e1dfca"
    rollbar.init(ROLLBAR_POST_CLIENT_ITEM, 'production', enabled=False)

    stripe.api_key = 'pk_test_6tMDkFKTz4N0wIFQZHuzOUyW'
    # stripe.api_key = 'pk_live_45dmSl66k4xLy4X4yfF3RVpd'

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
def scale(app_name, replicas, size):
    """
    Scale app.
    """
    try:
        gigalixir_app.scale(app_name, replicas, size)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@cli.command()
@click.argument('app_name')
@click.option('-r', '--rollback_id', default=None, help='The rollback id of the release to revert to. Use gigalixir get releases to find the rollback_id. If omitted, this defaults to the second most recent release.')
def rollback(app_name, rollback_id):
    """
    Rollback to a previous release. 
    """
    try:
        gigalixir_app.rollback(app_name, rollback_id)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@cli.command()
@click.argument('app_name')
def restart(app_name):
    """
    Restart app.
    """
    try:
        gigalixir_app.restart(app_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@cli.command()
@click.argument('app_name')
@click.argument('module')
@click.argument('function')
def run(app_name, module, function):
    """
    Run arbitrary function e.g. Elixir.Tasks.migrate/0.
    """
    try:
        gigalixir_app.run(app_name, module, function)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@update.command()
@click.argument('email')
@click.option('-p', '--current_password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-n', '--new_password', prompt=True, hide_input=True, confirmation_prompt=False)
def user(email, current_password, new_password):
    """
    Edit user. Currently only password is editable.
    """
    try:
        gigalixir_user.change_password(email, current_password, new_password)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@update.command()
@click.argument('email')
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-y', '--yes', is_flag=True)
def api_key(email, password, yes):
    """
    Regenerate a new api key to replace the old one.
    """
    try:
        gigalixir_api_key.regenerate(email, password, yes)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@cli.command()
@click.argument('email')
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-y', '--yes', is_flag=True)
def login(email, password, yes):
    """
    Login and receive an api key.
    """
    try:
        gigalixir_user.login(email, password, yes)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@get.command()
def ssh_keys():
    """
    Get your ssh keys.
    """
    try:
        gigalixir_ssh_key.get()
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@get.command()
def apps():
    """
    Get apps.
    """
    try:
        gigalixir_app.get()
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@get.command()
@click.argument('app_name')
def releases(app_name):
    """
    Get previous releases for app.
    """
    try:
        gigalixir_release.get(app_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@get.command()
@click.argument('app_name')
def permissions(app_name):
    """
    Get permissions for app.
    """
    try:
        gigalixir_permission.get(app_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@create.command()
@click.argument('ssh_key')
def ssh_key(ssh_key):
    """
    Create ssh key.
    """
    try:
        gigalixir_ssh_key.create(ssh_key)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@create.command()
@click.argument('app_name')
@click.argument('key')
@click.argument('value')
def config(app_name, key, value):
    """
    Create app configuration/environment variable.
    """
    try:
        gigalixir_config.create(app_name, key, value)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@get.command()
@click.argument('app_name')
def configs(app_name):
    """
    Get app configuration/environment variables.
    """
    try:
        gigalixir_config.get(app_name)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@delete.command()
@click.argument('key_id')
def ssh_key(key_id):
    """
    Deletes your ssh key. Find the key_id from gigalixir get ssh_keys.
    """
    try:
        gigalixir_ssh_key.delete(key_id)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@delete.command()
@click.argument('app_name')
@click.argument('email')
def permission(app_name, email):
    """
    Denies user access to app.
    """
    try:
        gigalixir_permission.delete(app_name, email)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@delete.command()
@click.argument('app_name')
@click.argument('key')
def config(app_name, key):
    """
    Delete app configuration/environment variables.
    """
    try:
        gigalixir_config.delete(app_name, key)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)

@create.command()
@click.argument('unique_name')
@click.argument('email')
def permission(unique_name, email):
    """
    Grants another user permission to collaborate on an app.
    """
    try:
        gigalixir_permission.create(unique_name, email)
    except:
        logging.error(sys.exc_info()[1])
        rollbar.report_exc_info()
        sys.exit(1)


@create.command()
@click.argument('unique_name')
def app(unique_name):
    """
    Create a new app.
    """
    try:
        gigalixir_app.create(unique_name)
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
def user(email, card_number, card_exp_month, card_exp_year, card_cvc, password, accept_terms_of_service_and_privacy_policy):
    """
    Create a new user.
    """
    try:
        gigalixir_user.create(email, card_number, card_exp_month, card_exp_year, card_cvc, password, accept_terms_of_service_and_privacy_policy)
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
