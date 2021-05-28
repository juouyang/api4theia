from flask import current_app
import docker
import os
from app.models import Users, Strategies
import subprocess as sp

client = docker.from_env()

def sync_containers_status():
    for strategy in Strategies.strategies:
        strategy['theia'] = "not running"
        if len(client.containers.list(all=True, filters={'name': strategy['sid']})) == 1:
            strategy['theia'] = "running"


def run_container(uid, sid, port):
    app = current_app._get_current_object()
    if (len(client.images.list(name=app.config['DOCKER_IMAGE'])) == 0):
        return "docker.errors.ImageNotFound"

    src_template = app.config['TEMPLATE_PROJECT']
    src_path = app.config['STORAGE_POOL'] + '/' + uid + '/' + sid + '/src'
    if not os.path.isdir(src_path):
        os.makedirs(src_path, exist_ok=True)
        if os.path.isdir(src_template):
            sp.call("cp -rf " + src_template + "/* " + src_path, shell=True)
            sp.call("mv -f " + src_path + '/Your_Strategy.py \"' +
                    src_path + '/' + sid + '.py\"', shell=True)
        with open(src_path + "/.gitignore", "w") as out:
            out.write(app.config['GIT_IGNORE'])
        os.makedirs(src_path + '/.sandbox', exist_ok=True)
        with open(src_path + '/.sandbox/01_hello_matplotlib.py', "w") as out:
            out.write(app.config['HELLO_MATPLOTLIB'])
        with open(src_path + '/.sandbox/02_hello_plotly.py', "w") as out:
            out.write(app.config['HELLO_PLOTLY'])
        with open(src_path + '/.sandbox/03_hello_tensorflow.py', "w") as out:
            out.write(app.config['HELLO_TENSORFLOW'])
        sp.call("cd " + src_path + ";" + app.config['GIT_INIT'], shell=True)
    else:
        if os.path.isdir(src_template):
            sp.call("cp -rf " + src_template +
                    "/reference/ " + src_path, shell=True)
            sp.call("cp -rf " + src_template +
                    "/__main__.py " + src_path, shell=True)

    theia_config_path = app.config['STORAGE_POOL'] + \
        '/' + uid + '/' + sid + '/theia_config'
    if not os.path.isdir(theia_config_path):
        os.makedirs(theia_config_path, exist_ok=True)

    if len(client.containers.list(all=True, filters={'name': sid})) == 0:
        try:
            user = [u for u in Users.users if u['uid'] == uid]
            if (len(user) != 1):
                raise Exception("user not found")
            client.containers.run(
                app.config['DOCKER_IMAGE'],
                auto_remove=True,
                detach=True,
                name=sid,
                ports={'443/tcp': port},
                volumes={
                    src_path + '/': {'bind': '/home/project/', 'mode': 'rw'},
                    theia_config_path + '/': {'bind': '/home/theia/.theia', 'mode': 'rw'},
                    '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
                    '/usr/bin/docker': {'bind': '/usr/bin/docker', 'mode': 'rw'}
                },
                mem_limit="3g",
                privileged=False,
                environment={
                    'USERNAME': user[0]['username'], 'PASSWORD': user[0]['password']}
            )
            return ""
        except:
            return "error when start container"


def remove_container(sid):
    if len(client.containers.list(all=True, filters={'name': sid})) != 0:
        container = client.containers.get(sid)
        container.stop(
            timeout=1
        )


def cleanup_volume(uid, sid):
    app = current_app._get_current_object()
    folderpath = app.config['STORAGE_POOL'] + '/' + uid + '/' + sid
    remove_container(sid)
    sp.call("rm -rf " + folderpath, shell=True)
