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

def test_everything():
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
            result = runner.invoke(gigalixir.cli, ['create'])
            assert result.exit_code == 0
            app_name = result.output.rstrip()
            gigalixir.shell.cast("git push gigalixir")
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
        result = runner.invoke(gigalixir.cli, ['status', app_name])
        assert result.exit_code == 0
        status = json.loads(result.output)
        assert status["replicas_desired"] == 1
        assert status["replicas_running"] == 1

        # set a config
        result = runner.invoke(gigalixir.cli, ['set_config', app_name, "FOO", "foo"])
        assert result.exit_code == 0

        # get configs
        result = runner.invoke(gigalixir.cli, ['configs', app_name])
        assert result.exit_code == 0
        configs = json.loads(result.output)
        assert configs == {"FOO": "foo"}

        # delete the config
        result = runner.invoke(gigalixir.cli, ['delete_config', app_name, "FOO"])
        assert result.exit_code == 0

        # get configs
        result = runner.invoke(gigalixir.cli, ['configs', app_name])
        assert result.exit_code == 0
        configs = json.loads(result.output)
        assert configs == {}

        # hot upgrade
        with cd("gigalixir-getting-started"):
            gigalixir.shell.cast("""git -c http.extraheader="GIGALIXIR-HOT:true" push gigalixir origin/v0.0.2:master""")
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
        result = runner.invoke(gigalixir.cli, ['scale', app_name, '--replicas=0'])
        assert result.exit_code == 0

        # check status
        result = runner.invoke(gigalixir.cli, ['status', app_name])
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

