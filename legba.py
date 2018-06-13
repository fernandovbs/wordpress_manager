#!/usr/bin/env python
import os
import json
from subprocess import run, PIPE
import click

def wp_cli_exists(path):
    try:
        p = run(['wp', 'core', 'is-installed'], cwd=path, stderr=PIPE)
    except FileNotFoundError:
        return False

    if p.stderr:
        return False

    return True

@click.group()
def cli():
   pass


''' Plugins list '''
@cli.command('plugins')
@click.argument('status')
@click.option('--context', '-c')
def plugins_command(status, context='host'):
    response = plugins(status, context)
    click.echo(response)


def plugins(status, context):
    command = ['wp', 'plugin', 'list', '--skip-themes']

    if status in ('active', 'inactive'):
        command.append(f'--status={status}')
    else: 
        command.append(f'--status=active')

    command.append('--format=json')

    response = loop_through(command)

    if context == 'global':
        response = parse_plugins_response(response)

    return response

def parse_plugins_response(response_from_command):
    hosts_quantity = len(response_from_command)
    plugins_dict = {}

    for host, plugins in response_from_command.items():
        plugins_list = json.loads(plugins)
        for x in range(len(plugins_list)):            
            if plugins_list[x]['name'] not in plugins_dict:
                plugins_dict[ plugins_list[x]['name'] ] = 1
            else:
                plugins_dict[ plugins_list[x]['name'] ] += 1

    response = [ plugin for plugin, quantity 
                 in plugins_dict.items()
                 if quantity == hosts_quantity
                ]
    
    return response

def loop_through(command):
    root_dir = '/srv/'
    response = {}

    for sub_dir in os.listdir(root_dir):
        path = os.path.abspath(os.path.join(root_dir,sub_dir))

        if wp_cli_exists(path):
            p = run(command, cwd=path,stdout=PIPE)
            if p.stdout:
                response[sub_dir] = p.stdout

    return response

if __name__ == "__main__":
    cli()

