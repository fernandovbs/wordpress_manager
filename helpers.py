import os
import json
import pyrebase
import click
import string
import re

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
            if 'legba4' == type_of_application(path):
                click.echo(f"Scanning {sub_dir} virtualhost now...")
                p = run(command, cwd=path, stdout=PIPE)
                if p.stdout:
                    click.echo('Done!')
                    vhost = sanitize_keys(sub_dir)
                    try:
                        if base:
                            response[vhost] = {base: json.loads(p.stdout.decode())}
                        else:
                            response[vhost] = json.loads(p.stdout.decode())
                    except:
                        if base:
                            response[vhost] = {base: 'erro'}
                        else:
                            response[vhost] = 'erro'                        


    return response

def wp_cli_exists(path):
    try:
        p = run(['wp', 'core', 'is-installed'], cwd=path, stdout=PIPE, stderr=PIPE)

        if p.stderr or 'Error' in p.stdout.decode():
            return False
    except:
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

def sanitize_keys(string_key):
    letters = string.ascii_letters
    return ''.join([i if i in letters else '_' for i in string_key])

def type_of_application(path):
    p = run(['git', 'config', '--get', 'remote.origin.url'], cwd=path, stdout=PIPE, stderr=PIPE)

    if p.stderr:
        return False
    remote_url = p.stdout.decode()
    if remote_url:
        if 'legba4' in remote_url:
            return 'legba4'
        if 'legba3' in remote_url: 
            return 'legba3'
        else:
            repo = re.split("[/.-_:]+", remote_url)
            return repo[-2] if len(repo) > 1 else False 
            
    return False
