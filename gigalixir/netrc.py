from __future__ import absolute_import
import netrc
import os
import platform

def netrc_name():
    if platform.system().lower() == 'windows':
        return "_netrc"
    else:
        return ".netrc"

def get_netrc_file():
    # TODO: support netrc files in locations other than ~/.netrc
    fname = os.path.join(os.environ['HOME'], netrc_name())
    try:
        netrc_file = netrc.netrc(fname)
    except IOError:
        # if netrc does not exist, touch it
        # from: http://stackoverflow.com/questions/1158076/implement-touch-using-python
        with open(fname, 'a'):
                os.utime(fname, None)
        netrc_file = netrc.netrc(fname)
    
    return netrc_file, fname

def clear_netrc():
    netrc_file, fname = get_netrc_file()

    del netrc_file.hosts['git.gigalixir.com'] 
    del netrc_file.hosts['api.gigalixir.com']
    with open(fname, 'w') as fp:
        fp.write(netrc_repr(netrc_file))

def update_netrc(email, key):
    netrc_file, fname = get_netrc_file()

    netrc_file.hosts['git.gigalixir.com'] = (email, None, key)
    netrc_file.hosts['api.gigalixir.com'] = (email, None, key)
    with open(fname, 'w') as fp:
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
