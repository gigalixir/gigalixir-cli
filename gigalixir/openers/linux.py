from gigalixir.shell import cast
import logging

class LinuxOpener(object):
    def open(self, url):
        logging.getLogger("gigalixir-cli").info("Running: xdg-open %s" % url)
        cast("xdg-open %s" % url)

