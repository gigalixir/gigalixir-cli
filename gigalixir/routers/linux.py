from gigalixir.shell import cast

class LinuxRouter(object):
    def route_to_localhost(self, ip):
        # cast("sudo iptables -t nat -L OUTPUT")
        cast("sudo iptables -t nat -A OUTPUT -p all -d %(ip)s -j DNAT --to-destination 127.0.0.1" % {"ip": ip})
    def unroute_to_localhost(self, ip):
        cast("sudo iptables -t nat -D OUTPUT -p all -d %(ip)s -j DNAT --to-destination 127.0.0.1" % {"ip": ip})
        # cast("sudo iptables -t nat -L OUTPUT")
