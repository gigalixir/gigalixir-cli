# This Python file uses the following encoding: utf-8
import os
from sure import expect
import subprocess
import gigalixir
import click
from click.testing import CliRunner
import httpretty

@httpretty.activate
def test_create_user():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/validate_email', body='{}', content_type='application/json')
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/free_users', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['signup', '--email=foo@gigalixir.com'], input="y\npassword\n")
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.httpretty.latest_requests[1].body).to.equal('{"password": "password", "email": "foo@gigalixir.com"}')

@httpretty.activate
def test_logout():
    runner = CliRunner()
    # Make sure this test does not modify the user's netrc file.
    with runner.isolated_filesystem():
        os.environ['HOME'] = '.'
        with open('.netrc', 'w') as f:
            f.write("""machine api.gigalixir.com
\tlogin foo@gigalixir.com
\tpassword fake-api-key
machine git.gigalixir.com
\tlogin foo@gigalixir.com
\tpassword fake-api-key
machine github.com
\tlogin foo
\tpassword fake-password
machine localhost
\tlogin foo@gigalixir.com
\tpassword fake-api-key
""")
            os.chmod(".netrc", 0o600)
        result = runner.invoke(gigalixir.cli, ['logout'])
        assert result.output == ''
        assert result.exit_code == 0
        with open('.netrc') as f:
            assert f.read() == """machine github.com
\tlogin foo
\tpassword fake-password
"""

@httpretty.activate
def test_login():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/login', body='{"data":{"key": "fake-api-key"}}', content_type='application/json')
    runner = CliRunner()

    # Make sure this test does not modify the user's netrc file.
    with runner.isolated_filesystem():
        os.environ['HOME'] = '.'
        result = runner.invoke(gigalixir.cli, ['login', '--email=foo@gigalixir.com'], input="password\ny\n")
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
    expect(httpretty.last_request().headers.headers).to.contain('Authorization: Basic Zm9vJTQwZ2lnYWxpeGlyLmNvbTpwYXNzd29yZA==\r\n')

@httpretty.activate
def test_login_escaping():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/login', body='{"data":{"key": "fake-api-key"}}', content_type='application/json')
    runner = CliRunner()

    # Make sure this test does not modify the user's netrc file.
    with runner.isolated_filesystem():
        os.environ['HOME'] = '.'
        result = runner.invoke(gigalixir.cli, ['login', '--email=foo@gigalixir.com'], input="p:assword\ny\n")
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
    expect(httpretty.last_request().headers.headers).to.contain('Authorization: Basic Zm9vJTQwZ2lnYWxpeGlyLmNvbTpwJTNBYXNzd29yZA==\r\n')

@httpretty.activate
def test_create_app():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/apps', body='{"data":{"unique_name":"fake-app-name"}}', content_type='application/json', status=201)
    runner = CliRunner()
    with runner.isolated_filesystem():
        subprocess.check_call(['git', 'init'])
        result = runner.invoke(gigalixir.cli, ['create', '--name=fake-app-name'])
        assert result.exit_code == 0
        remotes = subprocess.check_output(['git', 'remote', '-v'])
        assert remotes == """gigalixir\thttps://git.gigalixir.com/fake-app-name.git/ (fetch)
gigalixir\thttps://git.gigalixir.com/fake-app-name.git/ (push)
"""
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"unique_name": "fake-app-name"}')

def test_set_git_remote():
    runner = CliRunner()
    with runner.isolated_filesystem():
        subprocess.check_call(['git', 'init'])
        result = runner.invoke(gigalixir.cli, ['set_git_remote', 'fake-app-name'])
        assert result.exit_code == 0
        remotes = subprocess.check_output(['git', 'remote', '-v'])
        assert remotes == """gigalixir\thttps://git.gigalixir.com/fake-app-name.git/ (fetch)
gigalixir\thttps://git.gigalixir.com/fake-app-name.git/ (push)
"""

@httpretty.activate
def test_update_user():
    httpretty.register_uri(httpretty.PATCH, 'https://api.gigalixir.com/api/users', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['change_password', '--email=foo@gigalixir.com'], input="current_password\nnew_password\n")
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"new_password": "new_password"}')

@httpretty.activate
def test_get_apps():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/apps', body='{"data":[{"unique_name":"one","size":0.5,"replicas":1},{"unique_name":"two","size":0.5,"replicas":1},{"unique_name":"three","size":0.5,"replicas":1},{"unique_name":"four","size":0.5,"replicas":1},{"unique_name":"five","size":0.5,"replicas":1}]}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['apps'])
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
def test_scale_replicas_only():
    httpretty.register_uri(httpretty.PUT, 'https://api.gigalixir.com/api/apps/fake-app-name/scale', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['scale', 'fake-app-name', '--replicas=100'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"replicas": 100}')

@httpretty.activate
def test_scale():
    httpretty.register_uri(httpretty.PUT, 'https://api.gigalixir.com/api/apps/fake-app-name/scale', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['scale', 'fake-app-name', '--replicas=100', '--size=0.5'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"size": 0.5, "replicas": 100}')

@httpretty.activate
def test_restart():
    httpretty.register_uri(httpretty.PUT, 'https://api.gigalixir.com/api/apps/fake-app-name/restart', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['restart', 'fake-app-name'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_run():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/apps/fake-app-name/run', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['run', 'fake-app-name', 'Elixir.Tasks', 'migrate'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"function": "migrate", "module": "Elixir.Tasks"}')

@httpretty.activate
def test_get_configs():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/apps/fake-app-name/configs', body='{"data":{"DATABASE_URL":"ecto://user:pass@host:5432/db"}}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['configs', 'fake-app-name'])
    assert result.output == """{
  "DATABASE_URL": "ecto://user:pass@host:5432/db"
}
"""
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_create_config():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/apps/fake-app-name/configs', body='{}', content_type='application/json', status=201)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['set_config', 'fake-app-name', 'FOO', 'bar'])
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"value": "bar", "key": "FOO"}')

@httpretty.activate
def test_delete_config():
    httpretty.register_uri(httpretty.DELETE, 'https://api.gigalixir.com/api/apps/fake-app-name/configs', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['delete_config', 'fake-app-name', 'FOO'])
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"key": "FOO"}')

@httpretty.activate
def test_get_permissions():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/apps/fake-app-name/permissions', body='{"data":["foo@gigalixir.com"]}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['permissions', 'fake-app-name'])
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_create_permission():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/apps/fake-app-name/permissions', body='{}', content_type='application/json', status=201)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['add_permission', 'fake-app-name', 'foo@gigalixir.com'])
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"email": "foo@gigalixir.com"}')

@httpretty.activate
def test_delete_app():
    httpretty.register_uri(httpretty.DELETE, 'https://api.gigalixir.com/api/apps/fake-app-name', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['delete_app', 'fake-app-name'], input="y\n")
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_delete_permission():
    httpretty.register_uri(httpretty.DELETE, 'https://api.gigalixir.com/api/apps/fake-app-name/permissions', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['delete_permission', 'fake-app-name', 'foo@gigalixir.com'])
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"email": "foo@gigalixir.com"}')

@httpretty.activate
def test_create_api_key():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/api_keys', body='{"data":{"key":"another-fake-api-key","expires_at":"2017-04-28T16:47:09"}}', content_type='application/json', status=201)
    runner = CliRunner()
    # Make sure this test does not modify the user's netrc file.
    with runner.isolated_filesystem():
        os.environ['HOME'] = '.'
        result = runner.invoke(gigalixir.cli, ['reset_api_key', '--email=foo@gigalixir.com'], input="password\ny\n")
        assert result.exit_code == 0
        with open('.netrc') as f:
            assert f.read() == """machine api.gigalixir.com
\tlogin foo@gigalixir.com
\tpassword another-fake-api-key
machine git.gigalixir.com
\tlogin foo@gigalixir.com
\tpassword another-fake-api-key
machine localhost
\tlogin foo@gigalixir.com
\tpassword another-fake-api-key
"""
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().headers.headers).to.contain('Authorization: Basic Zm9vQGdpZ2FsaXhpci5jb206cGFzc3dvcmQ=\r\n')

@httpretty.activate
def test_get_releases():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/apps/fake-app-name/releases', body='{"data":[{"sha":"another-fake-sha","version":1,"created_at":"2017-03-29T17:28:29.000+00:00","summary":"fake summary"},{"sha":"fake-sha","version":2,"created_at":"2017-03-29T17:28:28.000+00:00","summary":"fake summary"}]}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['releases', 'fake-app-name'])
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    assert result.output == """[
  {
    "created_at": "2017-03-29T17:28:28.000+00:00", 
    "sha": "fake-sha", 
    "summary": "fake summary", 
    "version": 2
  }, 
  {
    "created_at": "2017-03-29T17:28:29.000+00:00", 
    "sha": "another-fake-sha", 
    "summary": "fake summary", 
    "version": 1
  }
]
"""

@httpretty.activate
def test_rollback_without_eligible_release():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/apps/fake-app-name/releases', body='{"data":[{"sha":"another-fake-sha","version":1,"created_at":"2017-03-29T17:28:29.000+00:00","summary":"fake summary"}]}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['rollback', 'fake-app-name'])
    assert result.exit_code != 0
    # expect(httpretty.has_request()).to.be.true
    expect(len(httpretty.httpretty.latest_requests)).to.equal(1)

@httpretty.activate
def test_rollback_without_version():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/apps/fake-app-name/releases', body='{"data":[{"sha":"another-fake-sha","version":3,"created_at":"2017-03-29T17:28:29.000+00:00","summary":"fake summary"},{"sha":"fake-sha","version":2,"created_at":"2017-03-29T17:28:28.000+00:00","summary":"fake summary"}]}', content_type='application/json')
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/apps/fake-app-name/releases/2/rollback', body='', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['rollback', 'fake-app-name'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_rollback():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/apps/fake-app-name/releases/1/rollback', body='', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['rollback', 'fake-app-name', '-r', '1'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_get_ssh_keys():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/ssh_keys', body='{"data":[{"key":"fake-ssh-key","id":1}]}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['ssh_keys'])
    assert result.output == """[
  {
    "id": 1, 
    "key": "fake-ssh-key"
  }
]
"""
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_create_ssh_key():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/ssh_keys', body='', content_type='application/json', status=201)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['add_ssh_key', 'fake-ssh-key'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"ssh_key": "fake-ssh-key"}')

@httpretty.activate
def test_delete_ssh_key():
    httpretty.register_uri(httpretty.DELETE, 'https://api.gigalixir.com/api/ssh_keys', body='', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['delete_ssh_key', '3'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"id": "3"}')

@httpretty.activate
def test_get_payment_method():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/payment_methods', body='{"data":{"last4":4242,"exp_year":2018,"exp_month":12,"brand":"Visa"}}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['payment_method'])
    assert result.output == """{
  "brand": "Visa", 
  "exp_month": 12, 
  "exp_year": 2018, 
  "last4": 4242
}
"""
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_update_payment_method():
    httpretty.register_uri(httpretty.POST, 'https://api.stripe.com/v1/tokens', body='{"id":"fake-stripe-token"}', content_type='application/json')
    httpretty.register_uri(httpretty.PUT, 'https://api.gigalixir.com/api/payment_methods', body='{}', content_type='application/json', status=200)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['set_payment_method', '--card_number=4111111111111111', '--card_exp_month=12', '--card_exp_year=34', '--card_cvc=123'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"stripe_token": "fake-stripe-token"}')


@httpretty.activate
def test_update_payment_method_cvc_leading_zero():
    httpretty.register_uri(httpretty.POST, 'https://api.stripe.com/v1/tokens', body='{"id":"fake-stripe-token"}', content_type='application/json')
    httpretty.register_uri(httpretty.PUT, 'https://api.gigalixir.com/api/payment_methods', body='{}', content_type='application/json', status=200)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['set_payment_method', '--card_number=4111111111111111', '--card_exp_month=12', '--card_exp_year=34', '--card_cvc=023'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.httpretty.latest_requests[0].body).to.equal('card%5Bnumber%5D=4111111111111111&card%5Bexp_year%5D=34&card%5Bcvc%5D=023&card%5Bexp_month%5D=12')
    expect(httpretty.last_request().body).to.equal('{"stripe_token": "fake-stripe-token"}')

@httpretty.activate
def test_logs():
    def log_response():
        from time import sleep
        for i in range(3):
            yield(u"%i 18:14:58.885 request_id=406arqcek0jjs7uo29o34o55sr841jec [info] Sent 200 in 197µs\n" % i)

    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/apps/fake-app-name/logs', body=log_response(), streaming=True)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['logs', 'fake-app-name'])
    assert result.output == u"\n".join([
        u"0 18:14:58.885 request_id=406arqcek0jjs7uo29o34o55sr841jec [info] Sent 200 in 197µs",
        u"1 18:14:58.885 request_id=406arqcek0jjs7uo29o34o55sr841jec [info] Sent 200 in 197µs",
        u"2 18:14:58.885 request_id=406arqcek0jjs7uo29o34o55sr841jec [info] Sent 200 in 197µs",
        u""
    ])
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_delete_domain():
    httpretty.register_uri(httpretty.DELETE, 'https://api.gigalixir.com/api/apps/fake-app-name/domains', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['delete_domain', 'fake-app-name', 'www.example.com'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"fqdn": "www.example.com"}')

@httpretty.activate
def test_get_domains():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/apps/fake-app-name/domains', body='{"data":["www.example.com"]}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['domains', 'fake-app-name'])
    assert result.output == """[
  "www.example.com"
]
"""
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_create_domain():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/apps/fake-app-name/domains', body='{}', content_type='application/json', status=201)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['add_domain', 'fake-app-name', 'www.example.com'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"fqdn": "www.example.com"}')

@httpretty.activate
def test_resend_confirmation_token():
    httpretty.register_uri(httpretty.PUT, 'https://api.gigalixir.com/api/users/reconfirm_email', body='{}', content_type='application/json', status=200)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['send_email_confirmation_token', '--email=foo@gigalixir.com'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"email": "foo@gigalixir.com"}')

@httpretty.activate
def test_get_reset_password_token():
    httpretty.register_uri(httpretty.PUT, 'https://api.gigalixir.com/api/users/reset_password', body='{}', content_type='application/json', status=200)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['send_reset_password_token', '--email=foo@gigalixir.com'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"email": "foo@gigalixir.com"}')

@httpretty.activate
def test_reset_password():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/users/reset_password', body='{}', content_type='application/json', status=200)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['set_password', '--token=fake-token'], input="password\n")
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"token": "fake-token", "password": "password"}')

@httpretty.activate
def test_invoices():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/invoices', body='{"data":[{"replica_size_seconds":43944,"period_start":"2017-05-11T22:57:34.000+00:00","period_end":"2017-05-12T22:57:34.000+00:00","paid":true,"app_name":"bar","amount_cents":82},{"replica_size_seconds":43200,"period_start":"2017-05-12T22:57:34.000+00:00","period_end":"2017-05-13T22:57:34.000+00:00","paid":true,"app_name":"bar","amount_cents":81},{"replica_size_seconds":43200,"period_start":"2017-05-13T22:57:34.000+00:00","period_end":"2017-05-14T22:57:34.000+00:00","paid":true,"app_name":"bar","amount_cents":81},{"replica_size_seconds":43200,"period_start":"2017-05-14T22:57:34.000+00:00","period_end":"2017-05-15T22:57:34.000+00:00","paid":true,"app_name":"bar","amount_cents":81},{"replica_size_seconds":43200,"period_start":"2017-05-15T22:57:34.000+00:00","period_end":"2017-05-16T22:57:34.000+00:00","paid":true,"app_name":"bar","amount_cents":81},{"replica_size_seconds":43200,"period_start":"2017-05-16T22:57:34.000+00:00","period_end":"2017-05-17T22:57:34.000+00:00","paid":false,"app_name":"bar","amount_cents":81}]}', content_type='application/json', status=200)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['invoices'])
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_current_period_usage():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/usage', body='{"data":[{"app":"foo","amount_cents":81}]}', content_type='application/json', status=200)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['current_period_usage'])
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_delete_database():
    httpretty.register_uri(httpretty.DELETE, 'https://api.gigalixir.com/api/apps/fake-app-name/databases/fake-database-id', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['delete_database', 'fake-app-name', 'fake-database-id'], input="y\n")
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_delete_free_database():
    httpretty.register_uri(httpretty.DELETE, 'https://api.gigalixir.com/api/apps/fake-app-name/free_databases/fake-database-id', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['delete_free_database', 'fake-app-name', 'fake-database-id'], input="y\n")
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_get_free_databases():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/apps/fake-app-name/free_databases', body="""
{
  "data": [
    {
      "username": "app",
      "url": "REDACTED",
      "state": "DELETED",
      "port": 5432,
      "password": "REDACTED",
      "id": "REDACTED",
      "host": "REDACTED",
      "database": "REDACTED",
      "app_name": "REDACTED"
    },
    {
      "username": "app",
      "url": "REDACTED",
      "state": "AVAILABLE",
      "port": 5432,
      "password": "REDACTED",
      "id": "REDACTED",
      "host": "REDACTED",
      "database": "REDACTED",
      "app_name": "REDACTED"
    }
  ]
}
""", content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['free_databases', 'fake-app-name'])
    print(result.output)
    assert result.output == """[
  {
    "app_name": "REDACTED", 
    "database": "REDACTED", 
    "host": "REDACTED", 
    "id": "REDACTED", 
    "password": "REDACTED", 
    "port": 5432, 
    "state": "DELETED", 
    "url": "REDACTED", 
    "username": "app"
  }, 
  {
    "app_name": "REDACTED", 
    "database": "REDACTED", 
    "host": "REDACTED", 
    "id": "REDACTED", 
    "password": "REDACTED", 
    "port": 5432, 
    "state": "AVAILABLE", 
    "url": "REDACTED", 
    "username": "app"
  }
]
"""
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_get_databases():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/apps/fake-app-name/databases', body="""
{
  "data": [
    {
      "username": "app",
      "state": "DELETED",
      "size": 0.6,
      "port": 5432,
      "password": "REDACTED",
      "id": "REDACTED",
      "host": "REDACTED",
      "database": "REDACTED",
      "app_name": "REDACTED"
    },
    {
      "username": "app",
      "state": "AVAILABLE",
      "size": 0.6,
      "port": 5432,
      "password": "REDACTED",
      "id": "REDACTED",
      "host": "REDACTED",
      "database": "REDACTED",
      "app_name": "REDACTED"
    }
  ]
}
""", content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['databases', 'fake-app-name'])
    print(result.output)
    assert result.output == """[
  {
    "app_name": "REDACTED", 
    "database": "REDACTED", 
    "host": "REDACTED", 
    "id": "REDACTED", 
    "password": "REDACTED", 
    "port": 5432, 
    "size": 0.6, 
    "state": "DELETED", 
    "username": "app"
  }, 
  {
    "app_name": "REDACTED", 
    "database": "REDACTED", 
    "host": "REDACTED", 
    "id": "REDACTED", 
    "password": "REDACTED", 
    "port": 5432, 
    "size": 0.6, 
    "state": "AVAILABLE", 
    "username": "app"
  }
]
"""
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_create_database():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/apps/fake-app-name/databases', body='{}', content_type='application/json', status=201)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['create_database', 'fake-app-name', '--size=4'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"size": 4.0}')

@httpretty.activate
def test_create_free_database():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/apps/fake-app-name/free_databases', body="""
{
  "data": {
    "username": "app",
    "url": "REDACTED",
    "state": "DELETED",
    "port": 5432,
    "password": "REDACTED",
    "id": "REDACTED",
    "host": "REDACTED",
    "database": "REDACTED",
    "app_name": "REDACTED"
  }
}
""", content_type='application/json', status=201)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['create_free_database', 'fake-app-name'])
    # mind the trailing spaces!!
    assert result.output == """{
  "app_name": "REDACTED", 
  "database": "REDACTED", 
  "host": "REDACTED", 
  "id": "REDACTED", 
  "password": "REDACTED", 
  "port": 5432, 
  "state": "DELETED", 
  "url": "REDACTED", 
  "username": "app"
}
"""
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_scale_database():
    httpretty.register_uri(httpretty.PUT, 'https://api.gigalixir.com/api/apps/fake-app-name/databases/fake-database-id', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['scale_database', 'fake-app-name', 'fake-database-id', '--size=8'])
    assert result.output == ''
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"size": 8.0}')

@httpretty.activate
def test_account():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/users', body='{"data":{}}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['account'])
    assert result.output == "{}\n"
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_upgrade():
    httpretty.register_uri(httpretty.PUT, 'https://api.gigalixir.com/api/users/upgrade', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['upgrade'], input="y\n")
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_get_log_drains():
    httpretty.register_uri(httpretty.GET, 'https://api.gigalixir.com/api/apps/fake-app-name/drains', body='{"data":[{"url":"syslog+tls://foo.papertrailapp.com:12345","token":"fake-token1","id":1},{"url":"https://user:pass@logs.timber.io/frames","token":"fake-token2","id":2}]}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['log_drains', 'fake-app-name'])
    print(result.output)
    assert result.output == """[
  {
    "id": 1, 
    "token": "fake-token1", 
    "url": "syslog+tls://foo.papertrailapp.com:12345"
  }, 
  {
    "id": 2, 
    "token": "fake-token2", 
    "url": "https://user:pass@logs.timber.io/frames"
  }
]
"""
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true

@httpretty.activate
def test_add_log_drain():
    httpretty.register_uri(httpretty.POST, 'https://api.gigalixir.com/api/apps/fake-app-name/drains', body='{}', content_type='application/json', status=201)
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['add_log_drain', 'fake-app-name', 'fake-url'])
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"url": "fake-url"}')

@httpretty.activate
def test_delete_log_drain():
    httpretty.register_uri(httpretty.DELETE, 'https://api.gigalixir.com/api/apps/fake-app-name/drains', body='{}', content_type='application/json')
    runner = CliRunner()
    result = runner.invoke(gigalixir.cli, ['delete_log_drain', 'fake-app-name', "10"])
    assert result.exit_code == 0
    expect(httpretty.has_request()).to.be.true
    expect(httpretty.last_request().body).to.equal('{"drain_id": "10"}')
