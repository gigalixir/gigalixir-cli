import os
import subprocess
import gigalixir
import click
from click.testing import CliRunner
import httpretty

@httpretty.activate
def test_create_user():
    httpretty.register_uri(httpretty.POST, 'https://api.stripe.com/v1/tokens', body='{"id":"fake-stripe-token"}', content_type='application/json')
    httpretty.register_uri(httpretty.POST, 'http://localhost:4000/api/users', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['create', 'user', '--email=foo@gigalixir.com', '--card_number=4111111111111111', '--card_exp_month=12', '--card_exp_year=34', '--card_cvc=123', '-y'], input="password\n")
    assert result.exit_code == 0

@httpretty.activate
def test_login():
    httpretty.register_uri(httpretty.GET, 'http://localhost:4000/api/login', body='{"key": "fake-api-key"}', content_type='application/json')
    runner = CliRunner()

    # Make sure this test does not modify the user's netrc file.
    with runner.isolated_filesystem():
        os.environ['HOME'] = '.'
        result = runner.invoke(gigalixir.cli, ['login', 'foo@gigalixir.com'], input="password\ny\n")
        assert result.exit_code == 0
        with open('.netrc') as f:
            assert f.read() == """machine api.gigalixir.com
\tlogin foo@gigalixir.com
\tpassword fake-api-key
machine git.gigalixir.com
\tlogin foo@gigalixir.com
\tpassword fake-api-key
machine localhost
\tlogin foo@gigalixir.com
\tpassword fake-api-key
"""

@httpretty.activate
def test_create_app():
    httpretty.register_uri(httpretty.POST, 'http://localhost:4000/api/apps', body='{}', content_type='application/json', status=201)
    runner = CliRunner()
    with runner.isolated_filesystem():
        subprocess.check_call(['git', 'init'])
        result = runner.invoke(gigalixir.cli, ['create', 'app', 'fake-app-name'])
        remotes = subprocess.check_output(['git', 'remote', '-v'])
        assert remotes == """gigalixir\thttps://git.gigalixir.com/fake-app-name.git/ (fetch)
gigalixir\thttps://git.gigalixir.com/fake-app-name.git/ (push)
"""
        assert result.exit_code == 0

@httpretty.activate
def test_edit_user():
    httpretty.register_uri(httpretty.PATCH, 'http://localhost:4000/api/users', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['edit', 'user', 'foo@gigalixir.com'], input="current_password\nnew_password\n")
    assert result.exit_code == 0

def test_ps():
    pass

def test_scale():
    pass

def test_restart():
    pass

def test_rollback():
    pass

def test_run():
    pass

def test_get_configs():
    pass

def test_create_config():
    pass

def test_delete_config():
    pass

def test_get_permissions():
    pass

def test_create_permission():
    pass

def test_delete_permission():
    pass

def test_create_api_key():
    pass

def test_get_releases():
    pass

def test_logs():
    pass

def test_get_ssh_keys():
    pass

def test_create_ssh_key():
    pass

def test_delete_ssh_key():
    pass

def test_get_payment_method():
    pass

def test_edit_payment_method():
    pass

