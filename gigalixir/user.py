import requests
import json
import netrc
import os
import logging
import click
import stripe

def create(email, card_number, card_exp_month, card_exp_year, card_cvc, password, accept_terms_of_service_and_privacy_policy):
    if not accept_terms_of_service_and_privacy_policy:
        logging.info("GIGALIXIR Terms of Service: FPO")
        logging.info("GIGALIXIR Privacy Policy: FPO")
        if not click.confirm('Do you accept the Terms of Service and Privacy Policy?'):
            raise Exception("Sorry, you must accept the Terms of Service and Privacy Policy to continue.")

    token = stripe.Token.create(
        card={
            "number": card_number,
            "exp_month": card_exp_month,
            "exp_year": card_exp_year,
            "cvc": card_cvc,
        },
    )
    r = requests.post('http://localhost:4000/api/users', headers = {
        'Content-Type': 'application/json',
    }, json = {
        'email': email,
        'password': password,
        'stripe_token': token["id"],
    })
    if r.status_code != 200:
        raise Exception(r.text)

def change_password(email, current_password, new_password):
    r = requests.patch('http://localhost:4000/api/users', auth = (email, current_password), json = {
        "new_password": new_password
    })
    if r.status_code == 401:
        raise Exception("Unauthorized")

    # TODO: might make sense to catch 422 and report errors more nicely than throwing up a stacktrace
    elif r.status_code != 200:
        raise Exception(r.text)

def login(email, password, yes):
    r = requests.get('http://localhost:4000/api/login', auth = (email, password))
    if r.status_code == 401:
        raise Exception("Unauthorized")
    elif r.status_code != 200:
        raise Exception(r.text)
    else:
        key = json.loads(r.text)["key"]
        if yes or click.confirm('Would you like to save your api key to your ~/.netrc file?'):
            # TODO: support netrc files in locations other than ~/.netrc
            try:
                netrc_file = netrc.netrc()
            except IOError:
                # if netrc does not exist, touch it
                # from: http://stackoverflow.com/questions/1158076/implement-touch-using-python
                fname = os.path.join(os.environ['HOME'], ".netrc")
                with open(fname, 'a'):
                        os.utime(fname, None)
                netrc_file = netrc.netrc()

            netrc_file.hosts['git.gigalixir.com'] = (email.encode('utf8'), None, key.encode('utf8'))
            netrc_file.hosts['localhost'] = (email.encode('utf8'), None, key.encode('utf8'))
            netrc_file.hosts['api.gigalixir.com'] = (email.encode('utf8'), None, key.encode('utf8'))
            file = os.path.join(os.environ['HOME'], ".netrc")
            with open(file, 'w') as fp:
                fp.write(netrc_repr(netrc_file))
        else:
            logging.info('Your api key is %s' % key)
            logging.warn('Many GIGALIXIR CLI commands will not work unless you your ~/.netrc file contains your GIGALIXIR credentials.')

# Copied from https://github.com/enthought/Python-2.7.3/blob/master/Lib/netrc.py#L105
# but uses str() instead of repr(). If the .netrc file uses quotes, repr will treat the quotes
# as part of the value and wrap it in another quote resulting in double quotes. I need to dig
# into this deeper, but this works for now.
def netrc_repr(netrc):
    rep = ""
    for host in netrc.hosts.keys():
        attrs = netrc.hosts[host]
        rep = rep + "machine "+ host + "\n\tlogin " + str(attrs[0]) + "\n"
        if attrs[1]:
            rep = rep + "account " + str(attrs[1])
        rep = rep + "\tpassword " + str(attrs[2]) + "\n"
    for macro in netrc.macros.keys():
        rep = rep + "macdef " + macro + "\n"
        for line in netrc.macros[macro]:
            rep = rep + line
        rep = rep + "\n"
    return rep
