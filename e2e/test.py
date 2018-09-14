# This Python file uses the following encoding: utf-8
import json
import os
import time
import subprocess
import gigalixir
import click
from click.testing import CliRunner
import contextlib
import logging
import requests
import timeit

def test_databases():
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    email = os.environ['GIGALIXIR_EMAIL']
    password = os.environ['GIGALIXIR_PASSWORD']
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.environ['HOME'] = os.getcwd()
        result = runner.invoke(gigalixir.cli, ['login', '--email=%s' % email], input="%s\ny\n" % password)
        assert result.exit_code == 0

        result = runner.invoke(gigalixir.cli, ['apps'])
        assert result.exit_code == 0
        # assumes this account already has an app created
        app = json.loads(result.output)[-1]
        assert app['replicas'] == 0
        app_name = app['unique_name']

        # ensure there is no available database at the start of the test.
        result = runner.invoke(gigalixir.cli, ['pg', '-a', app_name])
        assert result.exit_code == 0
        output = json.loads(result.output)
        for entry in output:
            if entry["state"] == "AVAILABLE":
                logging.info('Pass.')
                raise "there already exists an AVAILABLE database."

        # create
        result = runner.invoke(gigalixir.cli, ['pg:create', '-a', app_name])
        assert result.exit_code == 0

        database_id = None
        start_time = timeit.default_timer()
        database_id = wait_for_available_database(runner, app_name)
        print "database_id"
        print database_id
        elapsed = timeit.default_timer() - start_time
        logging.info("Elapsed time: %s" % elapsed)

        # scale
        result = runner.invoke(gigalixir.cli, ['pg:scale', database_id, '--size=1.7', '-a', app_name])
        assert result.exit_code == 0
        start_time = timeit.default_timer()
        wait_for_available_database(runner, app_name)
        elapsed = timeit.default_timer() - start_time
        logging.info("Elapsed time: %s" % elapsed)

        # delete
        result = runner.invoke(gigalixir.cli, ['pg:destroy', database_id, '-a', app_name], input="y\n")
        assert result.exit_code == 0

        start_time = timeit.default_timer()
        wait_for_deleted_database(runner, app_name, database_id)
        elapsed = timeit.default_timer() - start_time
        logging.info("Elapsed time: %s" % elapsed)

def test_mix():
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    email = os.environ['GIGALIXIR_EMAIL']
    password = os.environ['GIGALIXIR_PASSWORD']
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.environ['HOME'] = os.getcwd()
        result = runner.invoke(gigalixir.cli, ['login', '--email=%s' % email], input="%s\ny\n" % password)
        assert result.exit_code == 0
        with open(".tool-versions", "w") as text_file:
            text_file.write("elixir 1.5.1\nerlang 20.0")
        phx_new_process = subprocess.Popen(["mix", "phx.new", "gigalixir_scratch"], stdin=subprocess.PIPE)
        phx_new_process.communicate(input=b'n\n')
        with cd("gigalixir_scratch"):
            gigalixir.shell.cast("git init")
            gigalixir.shell.cast("git add .")
            gigalixir.shell.cast("git config user.email jesse@gigalixir.com")
            gigalixir.shell.cast("git config user.name Jesse")
            gigalixir.shell.cast("git commit -m phxnew")
            subprocess.check_call(["sed", "-i", "s/^\/config\/\*\.secret\.exs/# \/config\/*.secret.exs/", ".gitignore"])
            gigalixir.shell.cast("git add .gitignore")
            gigalixir.shell.cast("git add config/prod.secret.exs")
            gigalixir.shell.cast("git commit -m secrets")
            result = runner.invoke(gigalixir.cli, ['create'])
            assert result.exit_code == 0
            app_name = result.output.rstrip()
            gigalixir.shell.cast("git push gigalixir master")

            logging.info('Completed Deploy.')
            start_time = timeit.default_timer()
            url = 'https://%s.gigalixirapp.com/' % app_name
            for i in range(30):
                try:
                    logging.info('Attempt: %s/30: Checking %s' % (i, url))
                    r = requests.get(url)
                    if r.status_code != 200:
                        # wait 5 seconds
                        logging.info('Received %s' % r.status_code)
                        logging.info('Waiting 5 seconds to try again.')
                        time.sleep(5)
                    else:
                        logging.info('Pass.')
                        break
                except requests.exceptions.ConnectionError as e:
                    # wait 5 seconds
                    logging.info('ConnectionError: %s' % e)
                    logging.info('Waiting 5 seconds to try again.')
                    time.sleep(5)
            else:
                logging.info('Exhausted retries. Be sure to scale down your app manually and other necessary cleanup since we are aborting now.')
                assert False

            elapsed = timeit.default_timer() - start_time
            logging.info("Elapsed time: %s" % elapsed)

            # scale down to 0
            result = runner.invoke(gigalixir.cli, ['ps:scale', '--replicas=0'])
            assert result.exit_code == 0

def test_ruby():
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    email = os.environ['GIGALIXIR_EMAIL']
    password = os.environ['GIGALIXIR_PASSWORD']
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.environ['HOME'] = os.getcwd()
        result = runner.invoke(gigalixir.cli, ['login', '--email=%s' % email], input="%s\ny\n" % password)
        assert result.exit_code == 0
        gigalixir.shell.cast("git clone https://github.com/heroku/ruby-getting-started.git")
        with cd("ruby-getting-started"):
            result = runner.invoke(gigalixir.cli, ['create'])
            assert result.exit_code == 0
            app_name = result.output.rstrip()
            gigalixir.shell.cast("git push gigalixir master")

            logging.info('Completed Deploy.')
            start_time = timeit.default_timer()
            url = 'https://%s.gigalixirapp.com/' % app_name
            for i in range(30):
                try:
                    logging.info('Attempt: %s/30: Checking %s' % (i, url))
                    r = requests.get(url)
                    if r.status_code != 200:
                        # wait 5 seconds
                        logging.info('Received %s' % r.status_code)
                        logging.info('Waiting 5 seconds to try again.')
                        time.sleep(5)
                    else:
                        logging.info('Pass.')
                        break
                except requests.exceptions.ConnectionError as e:
                    # wait 5 seconds
                    logging.info('ConnectionError: %s' % e)
                    logging.info('Waiting 5 seconds to try again.')
                    time.sleep(5)
            else:
                logging.info('Exhausted retries. Be sure to scale down your app manually and other necessary cleanup since we are aborting now.')
                assert False

            elapsed = timeit.default_timer() - start_time
            logging.info("Elapsed time: %s" % elapsed)

            # scale down to 0
            result = runner.invoke(gigalixir.cli, ['ps:scale', '--replicas=0'])
            assert result.exit_code == 0

def test_no_assets():
    __test_deploy_and_upgrade(None, None, "js/no-assets")

def test_aws_us_east_1():
    __test_deploy_and_upgrade("aws", "us-east-1")

def test_deploy_and_upgrade():
    __test_deploy_and_upgrade(None, None)

def __test_deploy_and_upgrade(cloud, region, branch="master"):
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    email = os.environ['GIGALIXIR_EMAIL']
    password = os.environ['GIGALIXIR_PASSWORD']
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.environ['HOME'] = os.getcwd()
        result = runner.invoke(gigalixir.cli, ['login', '--email=%s' % email], input="%s\ny\n" % password)
        assert result.exit_code == 0
        gigalixir.shell.cast("git clone https://github.com/gigalixir/gigalixir-getting-started.git")
        with cd("gigalixir-getting-started"):
            gigalixir.shell.cast("git checkout %s" % branch)
            args = ['create']
            if cloud:
                args += ['--cloud=%s' % cloud]
            if region:
                args += ['--region=%s' % region]
            result = runner.invoke(gigalixir.cli, args)
            assert result.exit_code == 0
            app_name = result.output.rstrip()
            gigalixir.shell.cast("git push gigalixir HEAD:master")

            logging.info('Completed Deploy.')
            start_time = timeit.default_timer()
            url = 'https://%s.gigalixirapp.com/' % app_name
            for i in range(30):
                try:
                    logging.info('Attempt: %s/30: Checking %s' % (i, url))
                    r = requests.get(url)
                    if r.status_code != 200:
                        # wait 5 seconds
                        logging.info('Received %s' % r.status_code)
                        logging.info('Waiting 5 seconds to try again.')
                        time.sleep(5)
                    else:
                        logging.info('Pass.')
                        break
                except requests.exceptions.ConnectionError as e:
                    # wait 5 seconds
                    logging.info('ConnectionError: %s' % e)
                    logging.info('Waiting 5 seconds to try again.')
                    time.sleep(5)
            else:
                logging.info('Exhausted retries. Be sure to scale down your app manually and other necessary cleanup since we are aborting now.')
                assert False

            elapsed = timeit.default_timer() - start_time
            logging.info("Elapsed time: %s" % elapsed)

            # check status
            result = runner.invoke(gigalixir.cli, ['ps'])
            assert result.exit_code == 0
            status = json.loads(result.output)
            assert status["replicas_desired"] == 1
            assert status["replicas_running"] == 1

            # set a config
            result = runner.invoke(gigalixir.cli, ['config:set', "FOO=foo"])
            assert result.exit_code == 0

            # get configs
            result = runner.invoke(gigalixir.cli, ['config'])
            assert result.exit_code == 0
            configs = json.loads(result.output)
            assert configs == {"FOO": "foo"}

            # delete the config
            result = runner.invoke(gigalixir.cli, ['config:unset', "FOO"])
            assert result.exit_code == 0

            # get configs
            result = runner.invoke(gigalixir.cli, ['config'])
            assert result.exit_code == 0
            configs = json.loads(result.output)
            assert configs == {}

            # hot upgrade
            gigalixir.shell.cast("""git config user.email e2e@gigalixir.com""")
            gigalixir.shell.cast("""git config user.name e2e""")
            gigalixir.shell.cast("""git checkout v0.0.2""")
            gigalixir.shell.cast("""git rebase %s""" % branch)
            subprocess.check_call(["git", "-c", "http.extraheader=GIGALIXIR-HOT:true","push","gigalixir","HEAD:master"])

            logging.info('Completed Hot Upgrade.')
            start_time = timeit.default_timer()
            url = 'https://%s.gigalixirapp.com/' % app_name
            for i in range(30):
                try:
                    logging.info('Attempt: %s/30: Checking %s' % (i, url))
                    r = requests.get(url)
                    if r.status_code != 200:
                        # wait 5 seconds
                        logging.info('Received %s' % r.status_code)
                        logging.info('Waiting 5 seconds to try again.')
                        time.sleep(5)
                    else:
                        if "0.0.2" not in r.text:
                            # wait 5 seconds
                            logging.info('0.0.2 not found.')
                            logging.info('Waiting 5 seconds to try again.')
                            time.sleep(5)
                        else:
                            logging.info('Pass.')
                            break
                except requests.exceptions.ConnectionError as e:
                    # wait 5 seconds
                    logging.info('ConnectionError: %s' % e)
                    logging.info('Waiting 5 seconds to try again.')
                    time.sleep(5)
            else:
                logging.info('Exhausted retries. Be sure to scale down your app manually and other necessary cleanup since we are aborting now.')
                assert False
            elapsed = timeit.default_timer() - start_time
            logging.info("Elapsed time: %s" % elapsed)

            # scale down to 0
            result = runner.invoke(gigalixir.cli, ['ps:scale', '--replicas=0'])
            assert result.exit_code == 0

            # check status
            result = runner.invoke(gigalixir.cli, ['ps'])
            assert result.exit_code == 0
            status = json.loads(result.output)
            assert status["replicas_desired"] == 0
            assert status["replicas_running"] == 0

@contextlib.contextmanager
def cd(newdir, cleanup=lambda: True):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
        cleanup()

def wait_for_available_database(runner, app_name):
    for i in range(30):
        logging.info('Attempt: %s/30' % (i))
        result = runner.invoke(gigalixir.cli, ['pg', '-a', app_name])
        assert result.exit_code == 0
        output = json.loads(result.output)
        for entry in output:
            if entry["state"] == "AVAILABLE":
                logging.info('Pass.')
                return entry["id"]
        logging.info('Waiting 30 seconds to try again.')
        time.sleep(30)
    else:
        logging.info('Exhausted retries. Be sure to delete database manually and other necessary cleanup since we are aborting now.')
        assert False

def wait_for_deleted_database(runner, app_name, database_id):
    for i in range(30):
            logging.info('Attempt: %s/30' % (i))
            result = runner.invoke(gigalixir.cli, ['pg', '-a', app_name])
            assert result.exit_code == 0
            output = json.loads(result.output)
            for entry in output:
                if entry["id"] == database_id:
                    if entry["state"] == "DELETED":
                        logging.info('Pass.')
                        return
            logging.info('Waiting 30 seconds to try again.')
            time.sleep(30)
    else:
        logging.info('Exhausted retries. Be sure to delete database manually and other necessary cleanup since we are aborting now.')
        assert False

