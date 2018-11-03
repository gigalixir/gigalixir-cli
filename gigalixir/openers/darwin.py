from gigalixir.shell import cast
import logging

class DarwinOpener(object):
    def open(self, url):
        logging.getLogger("gigalixir-cli").info("Running: open %s" % url)
        cast("open %s" % url)

