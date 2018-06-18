import os
import pyrebase
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