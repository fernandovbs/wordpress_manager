import os
import json
import pyrebase
import click
from subprocess import run, PIPE
from dynaconf import settings

firebase_config = {
  "apiKey": settings.PYREBASE.apiKey,
  "authDomain": settings.PYREBASE.authDomain,
  "databaseURL": settings.PYREBASE.databaseURL,
  "storageBucket": settings.PYREBASE.storageBucket
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

def execute_bundle(command, base=''):
    root_dir = settings.PATH
    vhost_base = settings.VHOST_BASE if settings.VHOST_BASE  else ''
    response = {}

    for sub_dir in os.listdir(root_dir):
        path = os.path.abspath(os.path.join(root_dir,sub_dir, vhost_base))

        if os.path.isdir(path) and wp_cli_exists(path):
            click.echo(f"Scanning {sub_dir} virtualhost now...")
            p = run(command, cwd=path, stdout=PIPE)
            if p.stdout:
                click.echo('Done!')
                vhost = sanitize_keys(sub_dir)
                if base:
                    response[vhost] = {base: json.loads(p.stdout.decode())}
                else:
                    response[vhost] = json.loads(p.stdout.decode())

    return response

def wp_cli_exists(path):
    try:
        p = run(['wp', 'core', 'is-installed'], cwd=path, stderr=PIPE)
    except FileNotFoundError:
        return False

    if p.stderr:
        return False

    return True


def update_dataset(response):
    if db.child('data').child(settings.HOSTNAME).update(response):
        return True

    return False

def create_dataset(response):
    if db.child('data').child(settings.HOSTNAME).set(response):
        return True

    return False

def sanitize_keys(string):
    return ''.join([i if ord(i) < 128 else '_' for i in string])