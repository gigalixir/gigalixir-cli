import click
import json
from pygments import highlight, lexers, formatters

def echo_json(data):
    formatted_json = json.dumps(data, indent=2, sort_keys=True)
    colorful_json = highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
    click.echo(colorful_json)
