import logging
from . import auth
from . import presenter
import urllib
import json
import click
from six.moves.urllib.parse import quote

def get(session, app_name):
    r = session.get('/api/apps/%s/domains' % (quote(app_name.encode('utf-8'))))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        data = json.loads(r.text)["data"]
        presenter.echo_json(data)

def create(session, app_name, fqdn):
    r = session.post('/api/apps/%s/domains' % (quote(app_name.encode('utf-8'))), json = {
        "fqdn": fqdn,
    })
    if r.status_code != 201:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    data = json.loads(r.text)["data"]
    cname = data["cname"]
    logging.getLogger("gigalixir-cli").info("Added %s." % fqdn)
    logging.getLogger("gigalixir-cli").info("Create a CNAME or ALIAS record with your DNS provider pointing to %s" % cname)
    logging.getLogger("gigalixir-cli").info("Please give us a few minutes to set up a new TLS certificate.")


def delete(session, app_name, fqdn):
    r = session.delete('/api/apps/%s/domains' % (quote(app_name.encode('utf-8'))), json = {
        "fqdn": fqdn,
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
