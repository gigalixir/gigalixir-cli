import os
from gigalixir import gigalixir
import click
from click.testing import CliRunner
import httpretty

@httpretty.activate
def test_create_account():
    httpretty.register_uri(httpretty.POST, 'https://api.stripe.com/v1/tokens', body='{"id":"fake-stripe-token"}', content_type='application/json')
    httpretty.register_uri(httpretty.POST, 'http://localhost:4000/api/users', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['create', 'account', 'foo@gigalixir.com', '4111111111111111', '12', '34', '123', '-y'], input="password\n")
    assert result.exit_code == 0

@httpretty.activate
def test_login():
    httpretty.register_uri(httpretty.GET, 'http://localhost:4000/api/login', body='{"key": "fake-api-key"}', content_type='application/json')
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.environ['HOME'] = '.'
        # Make sure this test does not modify the user's netrc file.
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
