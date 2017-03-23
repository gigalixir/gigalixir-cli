from gigalixir import gigalixir
import click
from click.testing import CliRunner
import httpretty

@httpretty.activate
def test_create_account():
    httpretty.register_uri(httpretty.POST, 'https://api.stripe.com/v1/tokens', body='{"id":"tok_1A0Z2hEfFEDaO3aIXjE8hUJ9"}', content_type='application/json')
    httpretty.register_uri(httpretty.POST, 'http://localhost:4000/api/users', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['create', 'account', 'foo@gigalixir.com', '4111111111111111', '12', '34', '123', '-y'], input="password\n")
    assert result.exit_code == 0
    # assert result.output == ''
