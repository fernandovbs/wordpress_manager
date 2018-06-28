import json
import click
import helpers
from dynaconf import settings

''' Plugins list command'''
@click.command('plugins')
@click.option('--status', '-s')
@click.option('--context', '-c')
def plugins_command(status, context):
    response = plugins(status, context)

    if context == 'global':
        if response['plugins']['global']:
            click.echo('Global context!')        
            click.echo('Exporting to firebase...')

            data = helpers.db.child('data').child(settings.HOSTNAME).shallow().get()

            if data:
                click.echo(f'Updating {settings.HOSTNAME} information...')
                if helpers.update_dataset(response):
                    click.echo('Export complete!')
                else:
                    click.echo('Something goes wrong when exporting!')
            else:
                click.echo(f'Generating {settings.HOSTNAME} information...')
                if helpers.create_dataset(response):
                    click.echo('Export complete!')
                else:
                    click.echo('Something goes wrong when exporting!')
        else:
            click.echo('Nothing to export')
    else:
        click.echo(json.dumps(response))


def plugins(status, context):
    command = ['wp', 'plugin', 'list', '--skip-themes', '--format=json']
    response_payload = {}

    if status in ('active', 'inactive') and not context:
        command.append(f'--status={status}')
        response = helpers.execute_bundle(command)
        response_payload[status] = response
    elif context == 'global': 
        response_payload['plugins'] = execute_by_status(command)
        response_payload['plugins']['global'] = parse_common_plugins(response_payload['plugins'])
    else:
        response_payload = {'error': 'Check the parameters and try again'}        

    return response_payload


def execute_by_status(command):
    response = {}

    for status in ('active', 'inactive'):
        command.append(f'--status={status}')
        response[status] = helpers.execute_bundle(command, status)

    return response_bundle(response)


def response_bundle(response):
    response_bundle = {}
        
    for key, items in response['active'].items():
        if key not in response_bundle:
            response_bundle[key] = {}
        response_bundle[key]['active'] = items['active']

    for key, items in response['inactive'].items():
        if key not in response_bundle:
            response_bundle[key] = {}
        response_bundle[key]['inactive'] = items['inactive']

    return response_bundle

def parse_common_plugins(bundle):
    plugins_dict = {}

    for host, plugins_by_status in bundle.items():

        for status, plugins in plugins_by_status.items():
            for x in range(len(plugins)):
                plugin_name = helpers.sanitize_keys( plugins[x]['name'] )

                if plugin_name not in plugins_dict:
                    plugins_dict[ plugin_name ] = {
                        'active': {'quantidade': 0, 'hosts':[]}, 
                        'inactive': {'quantidade': 0, 'hosts':[]},
                    }

                plugins_dict[ plugin_name ][status]['quantidade'] += 1
                plugins_dict[ plugin_name ][status]['hosts'].append({'nome': host, 'versão': plugins[x]['version']})
                        
    return plugins_dict
