import requests
from . import auth
from . import presenter
import logging
import json
import qrcode
import click

def activate(host, yes):
    r = requests.post('%s/api/mfa/start' % host, headers = {
        'Content-Type': 'application/json',
    }, json = {
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        logging.getLogger("gigalixir-cli").info(data["message"])
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data["url"])
        qr.make(fit=True)
        qr.print_tty()

        # prompt for verification code
        token = click.prompt('Multi-factor Authentication Token')
        verify(host, token, yes)

def verify(host, token, yes):
    r = requests.post('%s/api/mfa/verify' % host, headers = {
        'Content-Type': 'application/json',
    }, json = {
        "mfa_token": token
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        message = data["message"]
        recovery_codes = data["recovery_codes"]
        click.echo(message)
        show_recovery_codes(recovery_codes, yes)

def show_recovery_codes(recovery_codes, yes):
    if yes or click.confirm('Are you ready to save your recovery codes?', default=True):
        presenter.echo_json(recovery_codes)
    else:
        logging.getLogger("gigalixir-cli").warn('Please save your recovery codes. To regenerate them, use `gigalixir account:mfa:recovery_codes:regenerate`.')
        
def deactivate(host):
    r = requests.delete('%s/api/mfa' % host, headers = {
        'Content-Type': 'application/json',
    }, json = {
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        message = data["message"]
        click.echo(message)

def regenerate_recovery_codes(host, yes):
    r = requests.post('%s/api/mfa/recovery_codes' % host, headers = {
        'Content-Type': 'application/json',
    }, json = {
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        recovery_codes = data["recovery_codes"]
        show_recovery_codes(recovery_codes, yes)
