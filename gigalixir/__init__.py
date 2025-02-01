from .shell import cast, call
from .routers.linux import LinuxRouter
from .routers.darwin import DarwinRouter
from .routers.windows import WindowsRouter
from .openers.linux import LinuxOpener
from .openers.darwin import DarwinOpener
from .openers.windows import WindowsOpener
from . import api_key as gigalixir_api_key
from . import api_session as gigalixir_api_session
from . import app_activity as gigalixir_app_activity
from . import app as gigalixir_app
from . import canary as gigalixir_canary
from . import config as gigalixir_config
from . import database as gigalixir_database
from . import domain as gigalixir_domain
from . import free_database as gigalixir_free_database
from . import invoice as gigalixir_invoice
from . import log_drain as gigalixir_log_drain
from . import mfa as gigalixir_mfa
from . import observer as gigalixir_observer
from . import payment_method as gigalixir_payment_method
from . import permission as gigalixir_permission
from . import release as gigalixir_release
from . import signup as gigalixir_signup
from . import ssh_key as gigalixir_ssh_key
from . import usage as gigalixir_usage
from . import user as gigalixir_user
from . import git
import click
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
import platform
from functools import wraps
import importlib.metadata

CLI_VERSION = importlib.metadata.version("gigalixir")

def _show_usage_error(self, file=None):
    if file is None:
        file = click._compat.get_text_stderr()
    color = None
    if self.ctx is not None:
        color = self.ctx.color
        click.echo(self.ctx.get_help() + '\n', file=file, color=color)
    click.echo('Error: %s' % self.format_message(), file=file, color=color)

click.exceptions.UsageError.show = _show_usage_error

ROLLBAR_POST_CLIENT_ITEM = "de505ce1f87d40fbbc299d479d2bfc2f"
# kinda sorta duplicated in this file as an option to cli Command.
# we need this at the "top" level so that handle_exception has access to rollbar
# when it was in cli(), it didn't work. I guess that gets run a bit later, after
# the command not found exception is raised.
env = os.environ.get("GIGALIXIR_ENV", "prod")
if env == "prod":
    rollbar.init(ROLLBAR_POST_CLIENT_ITEM, 'production',
                 enabled=True, allow_logging_basic_config=False,
                 code_version=CLI_VERSION)
elif env == "dev":
    rollbar.init(ROLLBAR_POST_CLIENT_ITEM, 'development', enabled=False, allow_logging_basic_config=False)
elif env == "test":
    rollbar.init(ROLLBAR_POST_CLIENT_ITEM, 'test', enabled=False, allow_logging_basic_config=False)
else:
    raise Exception("Invalid GIGALIXIR_ENV")

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
            version = CLI_VERSION
            rollbar.report_exc_info(sys.exc_info(), payload_data={"version": version})
            logging.getLogger("gigalixir-cli").error(sys.exc_info()[1])
            sys.exit(1)
    return wrapper

def rollbar_fingerprint(e):
    return e[1].__str__()

# TODO: remove localhost from .netrc file

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# copied from https://stackoverflow.com/questions/52213375/python-click-exception-handling-under-setuptools/52214480#52214480
def CatchAllExceptions(cls, handler):

    class Cls(cls):

        _original_args = None

        def make_context(self, info_name, args, parent=None, **extra):

            # grab the original command line arguments
            self._original_args = ' '.join(args)

            try:
                return super(Cls, self).make_context(
                    info_name, args, parent=parent, **extra)
            except Exception as exc:
                # call the handler
                handler(self, info_name, exc)

                # let the user see the original error
                raise

        def invoke(self, ctx):
            try:
                return super(Cls, self).invoke(ctx)
            except Exception as exc:
                # call the handler
                handler(self, ctx.info_name, exc)

                # let the user see the original error
                raise

    return Cls

def handle_exception(cmd, info_name, exc):
    msg = 'command:{} {} error:{}'.format(info_name, cmd._original_args, exc)
    rollbar.report_message(msg, 'warning')

class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        aliases = {
            "configs": "config",
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
        git.check_for_git()
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
        raise Exception("Could not detect app name. Try passing the app name explicitly with the `-a` flag or create an app with `gigalixir create`.")

@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
# @click.group(cls=CatchAllExceptions(AliasedGroup, handler=handle_exception), context_settings=CONTEXT_SETTINGS)
@click.option('--env', envvar='GIGALIXIR_ENV', default='prod', help="GIGALIXIR environment [prod, dev, test].")
@click.pass_context
def cli(ctx, env):
    ctx.obj = {}
    logging.basicConfig(format='%(message)s')
    logging.getLogger("gigalixir-cli").setLevel(logging.INFO)

    if env == "prod":
        stripe.api_key = 'pk_live_45dmSl66k4xLy4X4yfF3RVpd'
        host = "https://api.gigalixir.com"
    elif env == "dev":
        stripe.api_key = 'pk_test_6tMDkFKTz4N0wIFQZHuzOUyW'
        host = "http://localhost:4000"
    elif env == "test":
        stripe.api_key = 'pk_test_6tMDkFKTz4N0wIFQZHuzOUyW'

        # gets intercepted in tests
        host = "https://api.gigalixir.com"
    else:
        raise Exception("Invalid GIGALIXIR_ENV")

    ctx.obj['session'] = gigalixir_api_session.ApiSession(host, CLI_VERSION)
    ctx.obj['host'] = host
    ctx.obj['env'] = env

    PLATFORM = platform.system().lower() # linux, darwin, or windows
    if PLATFORM == "linux":
        ctx.obj['router'] = LinuxRouter()
        ctx.obj['opener'] = LinuxOpener()
    elif PLATFORM == "darwin":
        ctx.obj['router'] = DarwinRouter()
        ctx.obj['opener'] = DarwinOpener()
    elif PLATFORM == "windows":
        try:
            os.environ['HOME']
        except KeyError:
            os.environ['HOME'] = os.environ['USERPROFILE']
        ctx.obj['router'] = WindowsRouter()
        ctx.obj['opener'] = WindowsOpener()
    else:
        raise Exception("Unknown platform: %s" % PLATFORM)

# class TestException(Exception):
#     pass

# @cli.command(name="test")
# @click.pass_context
# @report_errors
# def app_info(ctx):
#     """
#     Test command for debugging
#     """
#     raise TestException("Test Exception")

def print_help(ctx, subcommand):
    if subcommand is None:
        click.echo(ctx.parent.get_help(), color=ctx.color)
    else:
        subcommand_obj = cli.get_command(ctx, subcommand)
        if subcommand_obj is None:
            click.echo("command %s not found" % subcommand)
        else:
            ctx.info_name = subcommand
            click.echo(subcommand_obj.get_help(ctx))

@cli.command()
@click.argument('subcommand', required=False)
@click.pass_context
@report_errors
def help(ctx, subcommand):
    """
    Show commands and descriptions.
    """
    print_help(ctx, subcommand)

@cli.command(name='ps')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def status(ctx, app_name):
    """
    Current app status.
    """
    gigalixir_app.status(ctx.obj['session'], app_name)

@cli.command(name='pg:scale')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-d', '--database_id', required=True)
@click.option('-s', '--size', type=float, help='Size of the database can be 0.6, 1.7, 4, 8, 16, 32, 48, 64, or 96.')
@click.option('--high_availability', help='Manage high availability. Set to "enabled" or "disabled"')
@click.pass_context
@report_errors
@detect_app_name
def scale_database(ctx, app_name, database_id, size, high_availability):
    """
    Scale database. Find the database id by running `gigalixir pg`
    """
    gigalixir_database.scale(ctx.obj['session'], app_name, database_id, size, high_availability)

@cli.command(name='ps:scale')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-r', '--replicas', type=int, help='Number of replicas to run.')
@click.option('-s', '--size', type=float, help='Size of each replica between 0.5 and 128 in increments of 0.1.')
@click.pass_context
@report_errors
@detect_app_name
def scale(ctx, app_name, replicas, size):
    """
    Scale app.
    """
    if not app_name:
        raise Exception("app_name is required")
    gigalixir_app.scale(ctx.obj['session'], app_name, replicas, size)

@cli.command(name='releases:rollback')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-r', '--version', default=None, help='The version of the release to revert to. Use gigalixir get releases to find the version. If omitted, this defaults to the second most recent release.')
@click.pass_context
@report_errors
@detect_app_name
def rollback(ctx, app_name, version):
    """
    Rollback to a previous release.
    """
    gigalixir_app.rollback(ctx.obj['session'], app_name, version)


@cli.command(name='ps:remote_console')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.option('-c', '--ssh_cmd', default="ssh", help='Which ssh command to use.')
@click.pass_context
@report_errors
@detect_app_name
def remote_console(ctx, app_name, ssh_opts, ssh_cmd):
    """
    Drop into a remote console on a live production node.
    """
    gigalixir_app.remote_console(ctx.obj['session'], app_name, ssh_opts, ssh_cmd)

@cli.command(name='ps:run')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.argument('command', nargs=-1)
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.option('-c', '--ssh_cmd', default="ssh", help='Which ssh command to use.')
@click.pass_context
@report_errors
@detect_app_name
def ps_run(ctx, app_name, ssh_opts, ssh_cmd, command):
    """
    Run a shell command on your running container.
    """
    gigalixir_app.ps_run(ctx.obj['session'], app_name, ssh_opts, ssh_cmd, *command)

@cli.command(name='ps:ssh')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.argument('command', nargs=-1)
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.option('-c', '--ssh_cmd', default="ssh", help='Which ssh command to use.')
@click.pass_context
@report_errors
@detect_app_name
def ssh(ctx, app_name, ssh_opts, ssh_cmd, command):
    """
    Ssh into app. Be sure you added your ssh key using gigalixir create ssh_key. Configs are not loaded automatically.
    """
    gigalixir_app.ssh(ctx.obj['session'], app_name, ssh_opts, ssh_cmd, *command)

@cli.command(name='ps:distillery')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.argument('distillery_command', nargs=-1)
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.option('-c', '--ssh_cmd', default="ssh", help='Which ssh command to use.')
@click.pass_context
@report_errors
@detect_app_name
def distillery(ctx, app_name, ssh_opts, ssh_cmd, distillery_command):
    """
    Runs a distillery command to run on the remote container e.g. ping, remote_console. Be sure you've added your ssh key.
    """
    gigalixir_app.distillery_command(ctx.obj['session'], app_name, ssh_opts, ssh_cmd, *distillery_command)

@cli.command(name='ps:restart')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def restart(ctx, app_name):
    """
    Restart app.
    """
    gigalixir_app.restart(ctx.obj['session'], app_name)


# gigalixir run mix ecto.migrate
@cli.command()
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.argument('command', nargs=-1)
@click.pass_context
@report_errors
@detect_app_name
def run(ctx, app_name, command):
    """
    Run shell command as a job in a separate process. Useful for migrating databases before the app is running.
    """
    gigalixir_app.run(ctx.obj['session'], app_name, command)

@cli.command(name='ps:migrate')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-m', '--migration_app_name', default=None, help='For umbrella apps, specify which inner app to migrate.')
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.option('-c', '--ssh_cmd', default="ssh", help='Which ssh command to use.')
@click.pass_context
@report_errors
@detect_app_name
def ps_migrate(ctx, app_name, migration_app_name, ssh_opts, ssh_cmd):
    """
    Run Ecto Migrations on a production node.
    """
    gigalixir_app.migrate(ctx.obj['session'], app_name, migration_app_name, ssh_opts, ssh_cmd)

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
    gigalixir_payment_method.update(ctx.obj['session'], card_number, card_exp_month, card_exp_year, card_cvc)

@cli.command(name='account:upgrade')
@click.option('--card_number', prompt=True)
@click.option('--card_exp_month', prompt=True)
@click.option('--card_exp_year', prompt=True)
@click.option('--card_cvc', prompt=True)
@click.option('--promo_code')
@click.pass_context
@report_errors
def upgrade(ctx, card_number, card_exp_month, card_exp_year, card_cvc, promo_code):
    """
    Upgrade from free tier to standard tier.
    """
    gigalixir_user.upgrade(ctx.obj['session'], card_number, card_exp_month, card_exp_year, card_cvc, promo_code)

@cli.command(name='account:destroy')
@click.option('-y', '--yes', is_flag=True)
@click.option('-e', '--email', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.pass_context
@report_errors
def destroy_account(ctx, yes, email, password):
    """
    Destroy your account
    """
    logging.getLogger("gigalixir-cli").info("WARNING: Deleting an account can not be undone.")
    if yes or click.confirm('Are you sure you want to delete your account (%s)?' % email):
        gigalixir_user.delete(ctx.obj['session'], email, password)

# @reset.command()
@cli.command(name='account:password:set')
@click.option('-t', '--token', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.pass_context
@report_errors
def set_password(ctx, token, password):
    """
    Set password using reset password token. Deprecated. Use the web form instead.
    """
    gigalixir_user.reset_password(ctx.obj['session'], token, password)

# @update.command()
@cli.command(name='account:password:change')
@click.option('-p', '--current_password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-n', '--new_password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.pass_context
@report_errors
def change_password(ctx, current_password, new_password):
    """
    Change password.
    """
    gigalixir_user.change_password(ctx.obj['session'], current_password, new_password)

@cli.command()
@click.pass_context
@report_errors
def account(ctx):
    """
    Account information.
    """
    gigalixir_user.account(ctx.obj['session'])

# @update.command()
@cli.command(name='account:api_key:reset')
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
def reset_api_key(ctx, password, yes):
    """
    Regenerate a replacement api key.
    """
    gigalixir_api_key.regenerate(ctx.obj['session'], password, yes, ctx.obj['env'])

@cli.command(name='account:mfa:activate')
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
def mfa_activate(ctx, yes):
    """
    Start the multi-factor authentication activation process.
    """
    gigalixir_mfa.activate(ctx.obj['session'], yes)


@cli.command(name='account:mfa:deactivate')
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
def mfa_deactivate(ctx, yes):
    """
    Deactivate multi-factor authentication.
    """
    if yes or click.confirm('Are you sure you want to deactivate multi-factor authentication?'):
        gigalixir_mfa.deactivate(ctx.obj['session'])

@cli.command(name='account:mfa:recovery_codes:regenerate')
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
def mfa_deactivate(ctx, yes):
    """
    Regenerate multi-factor authentication recovery codes.
    """
    gigalixir_mfa.regenerate_recovery_codes(ctx.obj['session'], yes)

@cli.command()
@click.pass_context
@report_errors
def logout(ctx):
    """
    Logout
    """
    gigalixir_user.logout(ctx.obj['env'])

@cli.command()
@click.option('-e', '--email', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-t', '--mfa_token', prompt=False) # we handle prompting if needed, not always needed
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
def login(ctx, email, password, yes, mfa_token):
    """
    Login and receive an api key.
    """
    gigalixir_user.login(ctx.obj['session'], email, password, yes, ctx.obj['env'], mfa_token)

@cli.command(name='login:google')
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
def google_login(ctx, yes):
    """
    Login with Google and receive an api key.
    """
    gigalixir_user.oauth_login(ctx.obj['session'], yes, ctx.obj['env'], 'google')

# @get.command()
@cli.command()
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-n', '--num')
@click.option('-t', '--no_tail', is_flag=True)
@click.pass_context
@report_errors
@detect_app_name
def logs(ctx, app_name, num, no_tail):
    """
    Stream logs from app.
    """
    gigalixir_app.logs(ctx.obj['session'], app_name, num, no_tail)

# @get.command()
@cli.command(name='account:payment_method')
@click.pass_context
@report_errors
def payment_method(ctx):
    """
    Get your payment method.
    """
    gigalixir_payment_method.get(ctx.obj['session'])

# @get.command()
@cli.command(name='drains')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def log_drains(ctx, app_name):
    """
    Get your log drains.
    """
    gigalixir_log_drain.get(ctx.obj['session'], app_name)


# @get.command()
@cli.command(name='account:ssh_keys')
@click.pass_context
@report_errors
def ssh_keys(ctx):
    """
    Get your ssh keys.
    """
    gigalixir_ssh_key.get(ctx.obj['session'])

@cli.command(name="apps:info")
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def app_info(ctx, app_name):
    """
    Get app info
    """
    gigalixir_app.info(ctx.obj['session'], app_name)

# @get.command()
@cli.command()
@click.pass_context
@report_errors
def apps(ctx):
    """
    Get apps.
    """
    gigalixir_app.get(ctx.obj['session'])

@cli.command(name='apps:activity')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def app_activity(ctx, app_name):
    """
    Get activity for an app.
    """
    gigalixir_app_activity.get(ctx.obj['session'], app_name)

# @get.command()
@cli.command()
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def releases(ctx, app_name):
    """
    Get previous releases for app.
    """
    gigalixir_release.get(ctx.obj['session'], app_name)


# @get.command()
@cli.command(name='access')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def permissions(ctx, app_name):
    """
    Get permissions for app.
    """
    gigalixir_permission.get(ctx.obj['session'], app_name)

# @create.command()
@cli.command(name='drains:add')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.argument('url')
@click.pass_context
@report_errors
@detect_app_name
def add_log_drain(ctx, app_name, url):
    """
    Add a drain to send your logs to.
    """
    gigalixir_log_drain.create(ctx.obj['session'], app_name, url)


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
    gigalixir_ssh_key.create(ctx.obj['session'], ssh_key)

# @create.command()
@cli.command(name='domains:add')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.argument('fully_qualified_domain_name')
@click.pass_context
@report_errors
@detect_app_name
def add_domain(ctx, app_name, fully_qualified_domain_name):
    """
    Adds a custom domain name to your app.
    """
    gigalixir_domain.create(ctx.obj['session'], app_name, fully_qualified_domain_name)

@cli.command(name="config:copy")
@click.option('-s', '--src_app_name', required=True)
@click.option('-d', '--dst_app_name', required=True)
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
# no detecting app name for this one
def config_copy(ctx, src_app_name, dst_app_name, yes):
    """
    Copy configuration variables from one app to another
    and restarts your app.
    """
    logging.getLogger("gigalixir-cli").info("WARNING: This will copy all configs from %s to %s. This might overwrite some configs in %s." % (src_app_name, dst_app_name, dst_app_name))
    if yes or click.confirm('Are you sure you want to continue?'):
        gigalixir_config.copy(ctx.obj['session'], src_app_name, dst_app_name)

@cli.command(name="config:set")
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('--no_restart', default=False, help="Do not restart the application.", is_flag=True)
@click.argument('assignments', nargs=-1)
@click.pass_context
@report_errors
@detect_app_name
def config_set(ctx, app_name, no_restart, assignments):
    """
    Set configuration variables and restarts your app.
    ASSIGNMENTS are of the form KEY=VALUE.
    For example,
    gigalixir config:set KEY0=VALUE0 KEY1="VALUE 1"
    """
    colored_keys = []
    configs = {}
    for assignment in assignments:
        try:
            key, value = assignment.split('=', 1)
            configs[key] = value
        except ValueError:
            print_help(ctx, "config:set")
            raise

    gigalixir_config.create_multiple(ctx.obj['session'], app_name, configs, no_restart)

# @get.command()
@cli.command(name='account:confirmation:resend')
@click.option('-e', '--email', prompt=True)
@click.pass_context
@report_errors
def send_email_confirmation_token(ctx, email):
    """
    Regenerate a email confirmation token and send to email.
    """
    gigalixir_user.get_confirmation_token(ctx.obj['session'], email)

# @get.command()
@cli.command(name='account:password:reset')
@click.option('-e', '--email', prompt=True)
@click.pass_context
@report_errors
def send_reset_password_token(ctx, email):
    """
    Send reset password token to email.
    """
    gigalixir_user.get_reset_password_token(ctx.obj['session'], email)

# @get.command()
@cli.command(name='account:email:set')
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=False)
@click.option('-e', '--email', prompt=True)
@click.pass_context
@report_errors
def send_reset_password_token(ctx, password, email):
    """
    Set account email
    """
    gigalixir_user.set_email(ctx.obj['session'], password, email)

# @get.command()
@cli.command(name='pg')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def databases(ctx, app_name):
    """
    Get databases for your app.
    """
    gigalixir_database.get(ctx.obj['session'], app_name)

# @get.command()
@cli.command(name='pg:read_replicas')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-d', '--database_id', required=True)
@click.pass_context
@report_errors
@detect_app_name
def read_replicas(ctx, app_name, database_id):
    """
    Get read replicas for your app and database.
    """
    gigalixir_database.get_read_replicas(ctx.obj['session'], app_name, database_id)

@cli.command(name='pg:read_replicas:create')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-d', '--database_id', required=True, help='The primary database id. Use "gigalixir pg" to find it.')
@click.option('-s', '--size', type=float, default=0.6, help='Size of the database can be 0.6, 1.7, 4, 8, 16, 32, 48, 64, or 96.')
@click.pass_context
@report_errors
@detect_app_name
def create_read_replica(ctx, app_name, database_id, size):
    """
    Create a new read replica for a database.
    """
    gigalixir_database.create_read_replica(ctx.obj['session'], app_name, database_id, size)



# @get.command()
@cli.command()
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def domains(ctx, app_name):
    """
    Get custom domains for your app.
    """
    gigalixir_domain.get(ctx.obj['session'], app_name)

# @get.command()
@cli.command()
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def config(ctx, app_name):
    """
    Get app configuration/environment variables.
    """
    gigalixir_config.get(ctx.obj['session'], app_name)

# @delete.command()
@cli.command(name='drains:remove')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.argument('drain_id')
@click.pass_context
@report_errors
@detect_app_name
def delete_log_drain(ctx, app_name, drain_id):
    """
    Deletes a log drain. Find the drain_id from gigalixir log_drains.
    """
    gigalixir_log_drain.delete(ctx.obj['session'], app_name, drain_id)

# @delete.command()
@cli.command(name='account:ssh_keys:remove')
@click.argument('key_id')
@click.pass_context
@report_errors
def delete_ssh_key(ctx, key_id):
    """
    Deletes your ssh key. Find the key_id from gigalixir get_ssh_keys.
    """
    gigalixir_ssh_key.delete(ctx.obj['session'], key_id)

@cli.command(name='apps:destroy')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
@detect_app_name
def delete_app(ctx, app_name, yes):
    """
    Deletes an app. Can not be undone.
    """
    logging.getLogger("gigalixir-cli").info("WARNING: Deleting an app can not be undone.")
    if yes or click.confirm('Do you want to delete your app (%s)?' % app_name):
        gigalixir_app.delete(ctx.obj['session'], app_name)

# @delete.command()
@cli.command(name='access:remove')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.argument('email')
@click.pass_context
@report_errors
@detect_app_name
def delete_permission(ctx, app_name, email):
    """
    Denies user access to app.
    """
    gigalixir_permission.delete(ctx.obj['session'], app_name, email)

# @delete.command()
@cli.command(name='pg:destroy')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-y', '--yes', is_flag=True)
@click.option('-d', '--database_id', required=True)
@click.pass_context
@report_errors
@detect_app_name
def delete_database(ctx, app_name, yes, database_id):
    """
    Delete database. Find the database id by running `gigalixir pg`
    """
    logging.getLogger("gigalixir-cli").info("WARNING: Deleting your database will destroy all your data and backups.")
    logging.getLogger("gigalixir-cli").info("WARNING: This can not be undone.")
    logging.getLogger("gigalixir-cli").info("WARNING: Please make sure you backup your data first.")
    if yes or click.confirm('Do you want to delete your database and all backups?'):
        gigalixir_database.delete(ctx.obj['session'], app_name, database_id)

# @delete.command()
@cli.command(name='domains:remove')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.argument('fully_qualified_domain_name')
@click.pass_context
@report_errors
@detect_app_name
def delete_domain(ctx, app_name, fully_qualified_domain_name):
    """
    Delete custom domain from your app.
    """
    gigalixir_domain.delete(ctx.obj['session'], app_name, fully_qualified_domain_name)

# @delete.command()
@cli.command(name='config:unset')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.argument('key')
@click.pass_context
@report_errors
@detect_app_name
def delete_config(ctx, app_name, key):
    """
    Delete app configuration/environment variables.
    """
    gigalixir_config.delete(ctx.obj['session'], app_name, key)

# @create.command()
@cli.command(name='access:add')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.argument('email')
@click.pass_context
@report_errors
@detect_app_name
def add_permission(ctx, app_name, email):
    """
    Grants a user permission to deploy an app.
    """
    gigalixir_permission.create(ctx.obj['session'], app_name, email)


@cli.command(name='pg:psql')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def pg_psql(ctx, app_name):
    """
    Connect to the database using psql
    """
    gigalixir_database.psql(ctx.obj['session'], app_name)

@cli.command(name='pg:create')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-s', '--size', type=float, default=0.6, help='Size of the database can be 0.6, 1.7, 4, 8, 16, 32, 48, 64, or 96.')
@click.option('-c', '--cloud')
@click.option('-r', '--region')
@click.option('-f', '--free', is_flag=True)
@click.option('-v', '--version', help='Major version (eg. POSTGRES_16). Not available for free databases.')
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
@detect_app_name
def create_database(ctx, app_name, size, cloud, region, free, version, yes):
    """
    Create a new database for app.
    """
    if free:
        if cloud != None or region != None:
            raise Exception("Sorry, free tier databases only run on gcp in us-central1. Try creating a standard database instead.")
        else:
            if yes or click.confirm("A word of caution: Free tier databases are not suitable for production and migrating from a free db to a standard db is not trivial. Do you wish to continue?"):
                gigalixir_free_database.create(ctx.obj['session'], app_name)
    else:
        gigalixir_database.create(ctx.obj['session'], app_name, size, cloud, region, version)

# @create.command()
@cli.command(name='git:remote')
@click.argument('app_name')
@click.pass_context
@report_errors
def set_git_remote(ctx, app_name):
    """
    Set the gigalixir git remote.
    """
    gigalixir_app.set_git_remote(ctx.obj['session'], app_name)

# @create.command()
@cli.command(name='apps:create')
@click.option('-n', '--name')
@click.option('-c', '--cloud')
@click.option('-r', '--region')
@click.option('-s', '--stack')
@click.pass_context
@report_errors
def create(ctx, name, cloud, region, stack):
    """
    Create a new app.
    """
    gigalixir_app.create(ctx.obj['session'], name, cloud, region, stack)

@cli.command(name='account:invoices')
@click.pass_context
@report_errors
def invoices(ctx):
    """
    List all previous invoices.
    """
    gigalixir_invoice.get(ctx.obj['session'])

@cli.command(name='account:usage')
@click.pass_context
@report_errors
def current_period_usage(ctx):
    """
    See the usage so far this month.
    """
    gigalixir_usage.get(ctx.obj['session'])

@cli.command(name='account:usage:running')
@click.pass_context
@report_errors
def current_running_usage(ctx):
    """
    See the current running charges.
    """
    gigalixir_usage.run_rate(ctx.obj['session'])

# @create.command()
@cli.command()
@click.pass_context
@report_errors
def signup(ctx):
    """
    Sign up for a new account.
    """
    gigalixir_signup.by_email(ctx)


@cli.command('signup:google')
@click.option('-y', '--accept_terms_of_service_and_privacy_policy', is_flag=True)
@click.pass_context
@report_errors
def google_signup(ctx, accept_terms_of_service_and_privacy_policy):
    """
    Sign up for a new account using your google login.
    """
    if not accept_terms_of_service_and_privacy_policy:
        logging.getLogger("gigalixir-cli").info("GIGALIXIR Terms of Service: https://www.gigalixir.com/terms")
        logging.getLogger("gigalixir-cli").info("GIGALIXIR Privacy Policy: https://www.gigalixir.com/privacy")
        if not click.confirm('Do you accept the Terms of Service and Privacy Policy?'):
            raise Exception("You must accept the Terms of Service and Privacy Policy to continue.")

    gigalixir_user.oauth_create(ctx.obj['session'], ctx.obj['env'], "google")

@cli.command(name='ps:observer')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-c', '--cookie')
@click.option('-o', '--ssh_opts', default="", help='Command-line options to pass to ssh.')
@click.option('-c', '--ssh_cmd', default="ssh", help='Which ssh command to use.')
@click.pass_context
@report_errors
@detect_app_name
def observer(ctx, app_name, cookie, ssh_opts, ssh_cmd):
    """
    Launch remote production observer.
    """
    gigalixir_observer.observer(ctx, app_name, cookie, ssh_opts, ssh_cmd)

@cli.command()
@click.pass_context
@report_errors
def version(ctx):
    """
    Show the CLI version.
    """
    click.echo(CLI_VERSION)


@cli.command(name='open')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def open_app(ctx, app_name):
    ctx.obj['opener'].open("https://%s.gigalixirapp.com" % app_name)

@cli.command(name='pg:backups')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-d', '--database_id', required=True)
@click.pass_context
@report_errors
@detect_app_name
def pg_backups(ctx, app_name, database_id):
    """
    List available backups. Find the database id by running `gigalixir pg`
    """
    gigalixir_database.backups(ctx.obj['session'], app_name, database_id)

@cli.command(name='pg:backups:restore')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-d', '--database_id', required=True)
@click.option('-b', '--backup_id', required=True)
@click.pass_context
@report_errors
@detect_app_name
def pg_backups_restore(ctx, app_name, database_id, backup_id):
    """
    Restore database from backup. Find the database id by running `gigalixir pg`
    """
    gigalixir_database.restore(ctx.obj['session'], app_name, database_id, backup_id)

@cli.command(name='pg:upgrade')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-d', '--database_id', required=True)
@click.argument('desired_version')
@click.pass_context
@report_errors
@detect_app_name
def pg_upgrade(ctx, app_name, database_id, desired_version):
    """
    Upgrade the major version of your database. Find the database id by running `gigalixir pg`
    """
    gigalixir_database.upgrade(ctx.obj['session'], app_name, database_id, desired_version)

@cli.command(name='stack:set')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-s', '--stack', required=True)
@click.pass_context
@report_errors
@detect_app_name
def set_stack(ctx, app_name, stack):
    """
    Set your app stack.
    """
    gigalixir_app.set_stack(ctx.obj['session'], app_name, stack)

@cli.command(name='canary')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.pass_context
@report_errors
@detect_app_name
def canary(ctx, app_name):
    """
    Get canary
    """
    gigalixir_canary.get(ctx.obj['session'], app_name)

@cli.command(name='canary:set')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-c', '--canary_name')
@click.option('-w', '--weight', type=int)
@click.pass_context
@report_errors
@detect_app_name
def set_canary(ctx, app_name, canary_name, weight):
    """
    Set a canary and weight for your app.
    """
    gigalixir_canary.set(ctx.obj['session'], app_name, canary_name, weight)

@cli.command(name='canary:unset')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-c', '--canary_name', required=True)
@click.pass_context
@report_errors
@detect_app_name
def unset_canary(ctx, app_name, canary_name):
    """
    Unset a canary for your app.
    """
    gigalixir_canary.delete(ctx.obj['session'], app_name, canary_name)

@cli.command(name='maintenance:on')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
@detect_app_name
def app_maintenance_on(ctx, app_name, yes):
    """
    Enables maintenance mode for an app.  App will be unreachable until maintenance mode is turned off.
    """
    if yes or click.confirm('Do you want to put your app (%s) in maintenance mode?' % app_name):
        gigalixir_app.maintenance(ctx.obj['session'], app_name, True)

@cli.command(name='maintenance:off')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
@detect_app_name
def app_maintenance_off(ctx, app_name, yes):
    """
    Disables maintenance mode on an app.
    """
    if yes or click.confirm('Do you want to remove your app (%s) from maintenance mode?' % app_name):
        gigalixir_app.maintenance(ctx.obj['session'], app_name, False)

@cli.command(name='ps:kill')
@click.option('-a', '--app_name', envvar="GIGALIXIR_APP")
@click.option('-p', '--pod', required=True, help='The name of the pod to kill.')
@click.option('-y', '--yes', is_flag=True)
@click.pass_context
@report_errors
@detect_app_name
def ps_kill(ctx, app_name, pod, yes):
    """
    Kills a pod.
    """
    if yes or click.confirm('Do you want to kill your pod (%s)?' % pod):
      gigalixir_app.kill_pod(ctx.obj['session'], app_name, pod)
