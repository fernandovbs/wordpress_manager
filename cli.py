#!/usr/bin/env python
import os
import json
import click
import pyrebase
from subprocess import run, PIPE
from dynaconf import settings

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


''' Plugins list command'''
@cli.command('plugins')
@click.argument('status')
@click.option('--context', '-c')
def plugins_command(status, context):
    response = plugins(status, context)
    click.echo(response)

def plugins(status, context):
    command = ['wp', 'plugin', 'list', '--skip-themes', '--format=json']

    if status in ('active', 'inactive'):
        command.append(f'--status={status}')
    else: 
        command.append(f'--status=active')

    response = execute_bundle(command)

    if context == 'global':
        response = parse_common_plugins(response)

    host = settings.HOSTNAME
    response_payload = {}
    response_payload[host] = response

    return json.dumps(response_payload)

def parse_common_plugins(plugins_by_host):
    hosts_quantity = len(plugins_by_host)
    plugins_dict = {}

    for host, plugins in plugins_by_host.items():

        plugins_list = json.loads(plugins)
        for x in range(len(plugins_list)):            
            if plugins_list[x]['name'] not in plugins_dict:
                plugins_dict[ plugins_list[x]['name'] ] = 1
            else:
                plugins_dict[ plugins_list[x]['name'] ] += 1

    response = {}
    response['plugins'] = [ {'name': plugin} for plugin, quantity 
                 in plugins_dict.items()
                 if quantity == hosts_quantity
               ]
    
    return response

def execute_bundle(command):
    root_dir = settings.PATH
    response = {}

    for sub_dir in os.listdir(root_dir):
        path = os.path.abspath(os.path.join(root_dir,sub_dir))

        if wp_cli_exists(path):
            p = run(command, cwd=path,stdout=PIPE)
            if p.stdout:
                response[sub_dir] = p.stdout.decode()

    return response

def wp_cli_exists(path):
    try:
        p = run(['wp', 'core', 'is-installed'], cwd=path, stderr=PIPE)
    except FileNotFoundError:
        return False

    if p.stderr:
        return False

    return True

if __name__ == "__main__":
    cli()