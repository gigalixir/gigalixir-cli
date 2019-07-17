from gigalixir.shell import cast
import logging

class WindowsRouter(object):
    def route_to_localhost(self, ip, epmd_port, distribution_port):
        logging.getLogger("gigalixir-cli").info("Setting up route")
        cast("route ADD %s MASK 255.255.255.255 127.0.0.1" % ip)

    def unroute_to_localhost(self, ip):
        logging.getLogger("gigalixir-cli").info("Cleaning up route")
        cast("route delete %s" % ip)
