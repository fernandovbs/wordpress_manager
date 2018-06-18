import json
import click
from dynaconf import settings
from helpers import execute_bundle, wp_cli_exists

''' Plugins list command'''
@click.command('plugins')
@click.option('--status', '-s')
@click.option('--context', '-c')
def plugins_command(status, context):
    response = plugins(status, context)
    click.echo(response)

def plugins(status, context):
    command = ['wp', 'plugin', 'list', '--skip-themes', '--format=json']
    host = settings.HOSTNAME
    response_payload = {}
    response_payload[host] = {}

    if status in ('active', 'inactive') and not context:
        command.append(f'--status={status}')
        response = execute_bundle(command)
        response_payload[host][status] = response
    elif context == 'global': 
        for status in ('active', 'inactive'):
            command.append(f'--status={status}')
            response = execute_bundle(command)
            response_payload[host][status] = response
        response_payload[host]['global'] = parse_common_plugins(response_payload[host])
    else:
        response_payload = {'error': 'Check the parameters and try again'}        

    return json.dumps(response_payload)

def parse_common_plugins(plugins_by_status):
    response = {}

    for status, plugins_by_host in plugins_by_status.items():
        hosts_quantity = len(plugins_by_host)
        plugins_dict = {}

        for host, plugins in plugins_by_host.items():
            plugins_list = json.loads(plugins)
            for x in range(len(plugins_list)):            
                if plugins_list[x]['name'] not in plugins_dict:
                    plugins_dict[ plugins_list[x]['name'] ] = 1
                else:
                    plugins_dict[ plugins_list[x]['name'] ] += 1
                    
        response[status] = [ {'name': plugin} for plugin, quantity 
                    in plugins_dict.items()
                    if quantity == hosts_quantity
                ]
    
    return response
