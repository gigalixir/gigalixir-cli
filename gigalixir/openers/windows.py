from gigalixir.shell import cast
import logging

class WindowsOpener(object):
    def open(self, url):
        logging.getLogger("gigalixir-cli").info("Running: start %s" % url)
        cast("start %s" % url)

