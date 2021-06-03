from flask import current_app
import docker
import os
from app.models import Users, Strategies
import subprocess as sp
import shortuuid
import socket
import requests

client = docker.from_env()

def sync_containers_status():
    for strategy in Strategies.strategies:
        strategy['theia'] = "not running"
        if len(client.containers.list(all=True, filters={'name': strategy['sid']})) == 1:
            strategy['theia'] = "running"


def prepare_python_project(uid, sid):
    app = current_app._get_current_object()
    src_template = app.config['TEMPLATE_PROJECT']
    src_path = app.config['STORAGE_POOL'] + '/strategies/' + uid + '/' + sid
    if not os.path.isdir(src_path):
        os.makedirs(src_path, exist_ok=True)
        if os.path.isdir(src_template):
            sp.call("cp -rf " + src_template + "/* " + src_path, shell=True)
            sp.call("mv -f " + src_path + '/Your_Strategy.py \"' +
                    src_path + '/' + sid + '.py\"', shell=True)
        with open(src_path + "/.gitignore", "w") as out:
            out.write(app.config['GIT_IGNORE'])
        # interactive
        os.makedirs(src_path + '/.sandbox/interactive', exist_ok=True)
        with open(src_path + '/.sandbox/interactive/01_hello_matplotlib.py', "w") as out:
            out.write(app.config['HELLO_MATPLOTLIB'])
        with open(src_path + '/.sandbox/interactive/02_hello_plotly.py', "w") as out:
            out.write(app.config['HELLO_PLOTLY'])
        with open(src_path + '/.sandbox/interactive/03_hello_scipy.py', "w") as out:
            out.write(app.config['HELLO_SCIPY'])
        with open(src_path + '/.sandbox/interactive/04_hello_pytorch.py', "w") as out:
            out.write(app.config['HELLO_PYTORCH'])
        # terminal
        os.makedirs(src_path + '/.sandbox/terminal', exist_ok=True)
        with open(src_path + '/.sandbox/terminal/01_hello_tensorflow.py', "w") as out:
            out.write(app.config['HELLO_TENSORFLOW'])
        with open(src_path + '/.sandbox/terminal/02_hello_talib.py', "w") as out:
            out.write(app.config['HELLO_TALIB'])
        with open(src_path + '/.sandbox/terminal/03_hello_statsmodel.py', "w") as out:
            out.write(app.config['HELLO_STATSMODEL'])
        with open(src_path + '/.sandbox/terminal/04_hello_quandl.py', "w") as out:
            out.write(app.config['HELLO_QUANDL'])
        with open(src_path + '/.sandbox/terminal/05_hello_caffe2.py', "w") as out:
            out.write(app.config['HELLO_CAFFE2'])
        sp.call("cd " + src_path + ";" + app.config['GIT_INIT'], shell=True)
    else:
        if os.path.isdir(src_template):
            sp.call("cp -rf " + src_template +
                    "/reference/ " + src_path, shell=True)
            sp.call("cp -rf " + src_template +
                    "/__main__.py " + src_path, shell=True)

    theia_config_path = app.config['STORAGE_POOL'] + \
        '/theia_config/' + uid + '/' + sid
    if not os.path.isdir(theia_config_path):
        os.makedirs(theia_config_path, exist_ok=True)
        with open(theia_config_path + '/settings.json', "w") as out:
            out.write("{\"python.showStartPage\": false}")


def run_container(uid, sid, port):
    app = current_app._get_current_object()
    if (len(client.images.list(name=app.config['DOCKER_IMAGE'])) == 0):
        return "docker.errors.ImageNotFound"

    prepare_python_project(uid, sid)

    if len(client.containers.list(all=True, filters={'name': uid + "-" + sid})) == 0:
        if (port == -1):
            return "cannot find unused port"
        try:
            user = [u for u in Users.users if u['uid'] == uid]
            username = user[0]['username'] if (len(user) == 1) else 'theia'
            onetime_password = shortuuid.ShortUUID().random(length=app.config['ONETIME_PW_LEN']) if (app.config['ONETIME_PW_ENABLED']) else ""
            client.containers.run(
                app.config['DOCKER_IMAGE'],
                auto_remove=True,
                detach=True,
                name=uid + "-" + sid,
                ports={'443/tcp': port},
                volumes={
                    app.config['STORAGE_POOL'] + '/strategies/' + uid + '/' + sid + '/': {'bind': '/home/project/', 'mode': 'rw'},
                    app.config['STORAGE_POOL'] + '/theia_config/' + uid + '/' + sid + '/': {'bind': '/home/theia/.theia', 'mode': 'rw'}
                },
                mem_limit="3g",
                privileged=False,
                environment={
                    'USERNAME': username,
                    'PASSWORD': onetime_password
                }
            )
            return onetime_password
        except:
            return "cannot start conatiner, maybe port: %i is used by other application" % port
    else:
        return "duplicate call"


def get_container_status(uid, sid):
    if len(client.containers.list(all=True, filters={'name': uid + "-" + sid})) != 0:
        container = client.containers.get(uid + "-" + sid)
        port = container.ports['443/tcp'][0]['HostPort']
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("127.0.0.1", int(port)))
        if result == 0:
            response = requests.get("https://127.0.0.1:" + str(port), verify=False)
            if response.status_code == 200 or response.status_code == 401:
                return "started"
            else:
                return "starting"
        else:
            return "starting"
    else:
        return "container not found"


def remove_container(uid, sid):
    if len(client.containers.list(all=True, filters={'name': uid + "-" + sid})) != 0:
        container = client.containers.get(uid + "-" + sid)
        port = container.ports['443/tcp'][0]['HostPort']
        container.stop(
            timeout=1
        )
        return port
    else:
        return "container not found"


def cleanup_volume(uid, sid):
    app = current_app._get_current_object()
    remove_container(uid, sid)
    src_path = app.config['STORAGE_POOL'] + '/strategies/' + uid + '/' + sid
    theia_config_path = app.config['STORAGE_POOL'] + '/theia_config/' + uid + '/' + sid
    sp.call("rm -rf " + src_path + " " + theia_config_path, shell=True)
    return ""