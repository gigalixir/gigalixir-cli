from __future__ import absolute_import
import netrc
import os

def clear_netrc():
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

    del netrc_file.hosts['git.gigalixir.com'] 
    del netrc_file.hosts['localhost']
    del netrc_file.hosts['api.gigalixir.com']
    file = os.path.join(os.environ['HOME'], ".netrc")
    with open(file, 'w') as fp:
        fp.write(netrc_repr(netrc_file))

def update_netrc(email, key):
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
