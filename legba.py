#!/usr/bin/env python
import os
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
@cli.command()
@click.argument('status')    
#@click.option('--context')
def plugins(status):
    command = f"wp plugin list --skip-themes --status={status} --format=json"
    response = loop_through(command)
    click.echo(response)

def loop_through(command):
    root_dir = '/srv/'
    response = {}
    total = 0
    for sub_dir in os.listdir(root_dir):
        path = os.path.abspath(os.path.join(root_dir,sub_dir))
        args = command.split()

        if wp_cli_exists(path):
            total += 1
            p = run(args, cwd=path,stdout=PIPE)
            if p.stdout:
                response[sub_dir] = p.stdout

    response['total'] = total

    return response

if __name__ == "__main__":
    cli()

