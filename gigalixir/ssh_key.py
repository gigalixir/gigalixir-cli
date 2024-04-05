from . import auth
from . import presenter
import json
import click
import logging

def ssh_keys(session):
    r = session.get('/api/ssh_keys')
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        return json.loads(r.text)["data"]

def get(session):
    data = ssh_keys(session)
    presenter.echo_json(data)

def create(session, key):
    r = session.post('/api/ssh_keys', json = {
        "ssh_key": key,
    })
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    logging.getLogger("gigalixir-cli").info('Please allow a few minutes for the SSH key to propagate to your run containers.')

def delete(session, key_id):
    r = session.delete('/api/ssh_keys', json = {
        "id": key_id
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
