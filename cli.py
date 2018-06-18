#!/usr/bin/env python
import click
from dynaconf import settings
from plugins import plugins_command as plugins

@click.group()
def cli():
   pass

cli.add_command(plugins)

if __name__ == "__main__":
    cli()