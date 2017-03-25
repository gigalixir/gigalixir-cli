from gigalixir.shell import cast
import subprocess

class DarwinRouter(object):
    def route_to_localhost(self, ip):
        """
        It's not great that we use "from any to any". It would be better to use
        from any to 10.244.7.124, but when I do that, erl fails to startup with
        Protocol 'inet_tcp': register/listen error: etimedout
        My guess is, it's trying to find epmd to register itself, but can't due to
        something in this file.
        """
        ps = subprocess.Popen(('echo', """
rdr pass on lo0 inet proto tcp from any to any port 4369 -> 127.0.0.1 port 4369
rdr pass on lo0 inet proto tcp from any to 10.244.7.124 port 36606 -> 127.0.0.1 port 36606
"""), stdout=subprocess.PIPE)
        subprocess.call(('sudo', 'pfctl', '-ef', '-'), stdin=ps.stdout)
        ps.wait()
        cast("sudo ifconfig lo0 10.244.7.124 netmask 255.255.255.255 alias")
        
    def unroute_to_localhost(self, ip):
        cast("sudo ifconfig lo0 10.244.7.124 netmask 255.255.255.255 -alias")
        subprocess.call("sudo pfctl -ef /etc/pf.conf".split())

