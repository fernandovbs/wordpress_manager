#!/usr/bin/env python
import click
import pyrebase
from dynaconf import settings
from plugins import plugins_command as plugins

config = {
  "apiKey": settings.PYREBASE.apiKey,
  "authDomain": settings.PYREBASE.authDomain,
  "databaseURL": settings.PYREBASE.databaseURL,
  "storageBucket": settings.PYREBASE.storageBucket
}

firebase = pyrebase.initialize_app(config)

@click.group()
def cli():
   pass

cli.add_command(plugins)

if __name__ == "__main__":
    cli()