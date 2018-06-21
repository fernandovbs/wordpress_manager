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
        click.echo('Global context!')        
        click.echo('Exporting to firebase...')

        data = helpers.db.child('data').get().val()

        if data and settings.HOSTNAME in data:
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
    active_bundle, inactive_bundle = (False, False)

    if response['active']:
        active_bundle = response['active'].popitem()
    if response['inactive']:
        inactive_bundle = response['inactive'].popitem()
        
    if active_bundle and inactive_bundle:
        response_bundle[active_bundle[0]] = {**active_bundle[1], **inactive_bundle[1]}
    elif active_bundle:
        response_bundle[active_bundle[0]] = active_bundle[1]
    elif inactive_bundle:
        response_bundle[inactive_bundle[0]] = inactive_bundle[1]       

    return response_bundle

def parse_common_plugins(bundle):
    response = {}

    for host, plugins_by_status in bundle.items():
        hosts_quantity = len(bundle)

        for status, plugins in plugins_by_status.items():
            plugins_dict = {}

            for x in range(len(plugins)):
                if plugins[x]['name'] not in plugins_dict:
                    plugins_dict[ plugins[x]['name'] ] = 1
                else:
                    plugins_dict[ plugins[x]['name'] ] += 1
                    
            response[status] = [{'name': plugin} for plugin, quantity in plugins_dict.items()
                                if quantity == hosts_quantity]
    
    return response
