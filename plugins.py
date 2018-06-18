#!/usr/bin/env python
import os
import json
import click
from subprocess import run, PIPE
from dynaconf import settings
from helpers import execute_bundle, wp_cli_exists

''' Plugins list command'''
@click.command('plugins')
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
