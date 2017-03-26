import os
from sure import expect
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
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.httpretty.latest_requests[0].body).to.equal('card%5Bnumber%5D=4111111111111111&card%5Bexp_year%5D=34&card%5Bcvc%5D=123&card%5Bexp_month%5D=12')
    expect(httpretty.httpretty.latest_requests[1].body).to.equal('{"stripe_token": "fake-stripe-token", "password": "password", "email": "foo@gigalixir.com"}')

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
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().headers.headers).to.contain('Authorization: Basic Zm9vQGdpZ2FsaXhpci5jb206cGFzc3dvcmQ=\r\n')

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
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"unique_name": "fake-app-name"}')

@httpretty.activate
def test_edit_user():
    httpretty.register_uri(httpretty.PATCH, 'http://localhost:4000/api/users', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['edit', 'user', 'foo@gigalixir.com'], input="current_password\nnew_password\n")
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"new_password": "new_password"}')

@httpretty.activate
def test_get_apps():
    httpretty.register_uri(httpretty.GET, 'http://localhost:4000/api/apps', body='[{"unique_name":"one","size_m":500,"replicas":1},{"unique_name":"two","size_m":500,"replicas":1},{"unique_name":"three","size_m":500,"replicas":1},{"unique_name":"four","size_m":500,"replicas":1},{"unique_name":"five","size_m":500,"replicas":1}]', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['get', 'apps'])
    assert result.output == """[
  {
    "name": "one", 
    "replicas": 1, 
    "size": 0.5
  }, 
  {
    "name": "two", 
    "replicas": 1, 
    "size": 0.5
  }, 
  {
    "name": "three", 
    "replicas": 1, 
    "size": 0.5
  }, 
  {
    "name": "four", 
    "replicas": 1, 
    "size": 0.5
  }, 
  {
    "name": "five", 
    "replicas": 1, 
    "size": 0.5
  }
]
"""
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_scale():
    httpretty.register_uri(httpretty.PUT, 'http://localhost:4000/api/apps/fake-app-name/scale', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['scale', 'fake-app-name', '--replicas=100', '--size=0.5'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"size": 500, "replicas": 100}')

@httpretty.activate
def test_restart():
    httpretty.register_uri(httpretty.PUT, 'http://localhost:4000/api/apps/fake-app-name/restart', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['restart', 'fake-app-name'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_run():
    httpretty.register_uri(httpretty.PUT, 'http://localhost:4000/api/apps/fake-app-name/run', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['run', 'fake-app-name', 'Elixir.Tasks', 'migrate'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"function": "migrate", "module": "Elixir.Tasks"}')

@httpretty.activate
def test_get_configs():
    httpretty.register_uri(httpretty.GET, 'http://localhost:4000/api/apps/fake-app-name/configs', body='{"DATABASE_URL":"ecto://user:pass@host:5432/db"}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['get', 'configs', 'fake-app-name'])
    assert result.output == """{
  "DATABASE_URL": "ecto://user:pass@host:5432/db"
}
"""
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

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

@httpretty.activate
def test_rollback():
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

