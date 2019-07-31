from gigalixir.shell import cast
import logging
import subprocess

class DarwinRouter(object):
    def route_to_localhost(self, ip, epmd_port, distribution_port):
        """
        It's not great that we use "from any to any". It would be better to use
        from any to 10.244.7.124, but when I do that, erl fails to startup with
        Protocol 'inet_tcp': register/listen error: etimedout
        My guess is, it's trying to find epmd to register itself, but can't due to
        something in this file.
        """
        logging.getLogger("gigalixir-cli").info("Setting up pfctl")
        logging.getLogger("gigalixir-cli").info("If prompted, please enter your sudo password:")
        ps = subprocess.Popen(('echo', """
rdr pass on lo0 inet proto tcp from any to any port %s -> 127.0.0.1 port %s
rdr pass on lo0 inet proto tcp from any to %s port %s -> 127.0.0.1 port %s
""" % (epmd_port, epmd_port, ip, distribution_port, distribution_port)), stdout=subprocess.PIPE)
        subprocess.call(('sudo', 'pfctl', '-ef', '-'), stdin=ps.stdout)
        ps.wait()
        cast("sudo ifconfig lo0 %s netmask 255.255.255.255 alias" % ip)
        
    def unroute_to_localhost(self, ip):
        logging.getLogger("gigalixir-cli").info("Cleaning up pfctl")
        logging.getLogger("gigalixir-cli").info("If prompted, please enter your sudo password:")
        cast("sudo ifconfig lo0 %s netmask 255.255.255.255 -alias" % ip)
        subprocess.call("sudo pfctl -ef /etc/pf.conf".split())

    def supports_multiplexing(self):
        return True
