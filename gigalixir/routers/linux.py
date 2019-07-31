from gigalixir.shell import cast
import logging

class LinuxRouter(object):
    def route_to_localhost(self, ip, epmd_port, distribution_port):
        logging.getLogger("gigalixir-cli").info("Setting up iptables")
        logging.getLogger("gigalixir-cli").info("If prompted, please enter your sudo password:")
        # cast("sudo iptables -t nat -L OUTPUT")
        cast("sudo iptables -t nat -A OUTPUT -p all -d %(ip)s -j DNAT --to-destination 127.0.0.1" % {"ip": ip})

    def unroute_to_localhost(self, ip):
        logging.getLogger("gigalixir-cli").info("Cleaning up iptables")
        logging.getLogger("gigalixir-cli").info("If prompted, please enter your sudo password:")
        cast("sudo iptables -t nat -D OUTPUT -p all -d %(ip)s -j DNAT --to-destination 127.0.0.1" % {"ip": ip})
        # cast("sudo iptables -t nat -L OUTPUT")

    def supports_multiplexing(self):
        return True
