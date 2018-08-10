import click
import json
from pygments import highlight, lexers, formatters

# Fix Python 2.x.
from six import u as unicode

def echo_json(data):
    formatted_json = json.dumps(data, indent=2, sort_keys=True)
    colorful_json = highlight(unicode(formatted_json), lexers.JsonLexer(), formatters.TerminalFormatter())
    click.echo(colorful_json)
