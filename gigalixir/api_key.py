import requests
from . import netrc
import json
import click
import logging

def regenerate(host, email, password, yes):
    r = requests.post('%s/api/api_keys' % host, auth = (email, password))
    if r.status_code == 401:
        raise Exception("Unauthorized")
    elif r.status_code != 201:
        raise Exception(r.text)
    else:
        key = json.loads(r.text)["data"]["key"]
        if yes or click.confirm('Would you like to save your api key to your ~/.netrc file?'):
            netrc.update_netrc(email, key)
        else:
            logging.info('Your api key is %s' % key)
            logging.warn('Many GIGALIXIR CLI commands may not work unless you your ~/.netrc file contains your GIGALIXIR credentials.')

