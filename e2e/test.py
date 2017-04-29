# This Python file uses the following encoding: utf-8
import os
import time
import subprocess
import gigalixir
import click
from click.testing import CliRunner
import contextlib
import logging
import requests

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
        url = 'https://%s.gigalixirapp.com/' % app_name
        for i in range(30):
            try:
                logging.info('Attempt: %s/30: Checking %s' % (i, url))
                r = requests.get(url)
                if r.status_code != 200:
                    # wait 5 seconds
                    logging.info('Received %s' % r.status_code)
                    logging.info('Waiting 30 seconds to try again.')
                    time.sleep(30)
                else:
                    logging.info('Pass.')
                    break
            except requests.exceptions.ConnectionError as e:
                # wait 5 seconds
                logging.info('ConnectionError: %s' % e)
                logging.info('Waiting 30 seconds to try again.')
                time.sleep(30)
        else:
            logging.info('Exhausted retries.')
            assert False

        # TODO: scale down to 0
        # TODO: delete?

@contextlib.contextmanager
def cd(newdir, cleanup=lambda: True):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
        cleanup()

