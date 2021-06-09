from docker.types import containers
from flask import current_app
import docker
import os
from app.models import Users, Strategies, Ports
import subprocess as sp
import shortuuid
import socket
import requests
import shutil
import glob
import threading
import time

client = docker.from_env()

def sync_containers_status():
    for strategy in Strategies.strategies:
        strategy['theia'] = "not running"
        if len(client.containers.list(all=True, filters={'name': strategy['sid']})) == 1:
            strategy['theia'] = "running"


def change_strategy_name(uid, sid, oldname, newname):
    app = current_app._get_current_object()
    src_path = app.config['STORAGE_POOL'] + '/strategies/' + uid + '/' + sid
    if (not os.path.exists(src_path)):
        prepare_python_project(uid, sid)
    old_file = os.path.join(src_path, oldname + '.py')
    new_file = os.path.join(src_path, newname + '.py')
    shutil.move(old_file, new_file)


def prepare_python_project(uid, sid):
    app = current_app._get_current_object()
    strategy_list = [s for s in Strategies.strategies if s['sid'] == sid]
    sname = strategy_list[0]['name'] if (len(strategy_list) == 1) else sid
    src_template = app.config['TEMPLATE_PROJECT']
    src_path = app.config['STORAGE_POOL'] + '/strategies/' + uid + '/' + sid
    if not os.path.isdir(src_path):
        os.makedirs(src_path, exist_ok=True)
        if os.path.isdir(src_template):
            sp.run(['cp', '-r'] + glob.glob(src_template + '/*') + [src_path])
            old_file = os.path.join(src_path, "Your_Strategy.py")
            new_file = os.path.join(src_path, sname + '.py')
            os.rename(old_file, new_file)
        with open(src_path + "/.gitignore", "w") as out:
            out.write(app.config['GIT_IGNORE'])
        sp.call(app.config['GIT_INIT'], shell=True, cwd = src_path)
    else:
        if os.path.isdir(src_template):
            sp.call(['cp', '-rf', src_template + "/reference/", src_path], shell=False)
            sp.call(['cp', '-rf', src_template + "/__main__.py", src_path], shell=False)

    theia_config_path = app.config['STORAGE_POOL'] + \
        '/theia_config/' + uid + '/' + sid
    if not os.path.isdir(theia_config_path):
        os.makedirs(theia_config_path, exist_ok=True)
        with open(theia_config_path + '/settings.json', "w") as out:
            out.write("{\"python.showStartPage\": false}")
        os.makedirs(theia_config_path + '/.theia', exist_ok=True)
        with open(theia_config_path + "/.theia/launch.json", "w") as out:
            out.write(app.config['DEBUG_SETTING'] % sid)
        # interactive
        os.makedirs(theia_config_path + '/.sandbox/interactive', exist_ok=True)
        with open(theia_config_path + '/.sandbox/interactive/01_hello_matplotlib.py', "w") as out:
            out.write(app.config['HELLO_MATPLOTLIB'])
        with open(theia_config_path + '/.sandbox/interactive/02_hello_plotly.py', "w") as out:
            out.write(app.config['HELLO_PLOTLY'])
        with open(theia_config_path + '/.sandbox/interactive/03_hello_scipy.py', "w") as out:
            out.write(app.config['HELLO_SCIPY'])
        with open(theia_config_path + '/.sandbox/interactive/04_hello_pytorch.py', "w") as out:
            out.write(app.config['HELLO_PYTORCH'])
        # terminal
        os.makedirs(theia_config_path + '/.sandbox/terminal', exist_ok=True)
        with open(theia_config_path + '/.sandbox/terminal/01_hello_tensorflow.py', "w") as out:
            out.write(app.config['HELLO_TENSORFLOW'])
        with open(theia_config_path + '/.sandbox/terminal/02_hello_talib.py', "w") as out:
            out.write(app.config['HELLO_TALIB'])
        with open(theia_config_path + '/.sandbox/terminal/03_hello_statsmodel.py', "w") as out:
            out.write(app.config['HELLO_STATSMODEL'])
        with open(theia_config_path + '/.sandbox/terminal/04_hello_quandl.py', "w") as out:
            out.write(app.config['HELLO_QUANDL'])
        with open(theia_config_path + '/.sandbox/terminal/05_hello_caffe2.py', "w") as out:
            out.write(app.config['HELLO_CAFFE2'])


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
                    app.config['STORAGE_POOL'] + '/strategies/' + uid + '/' + sid + '/': {'bind': '/home/project/' + sid + '/', 'mode': 'rw'},
                    app.config['STORAGE_POOL'] + '/theia_config/' + uid + '/' + sid + '/.theia/launch.json': {'bind': '/home/project/.theia/launch.json', 'mode': 'rw'},
                    app.config['STORAGE_POOL'] + '/theia_config/' + uid + '/' + sid + '/.sandbox': {'bind': '/home/project/.sandbox', 'mode': 'rw'},
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
        except Exception as e:
            return str(e) + ", cannot start conatiner at port: %i" % port
    else:
        return "container exist"


def get_container_status(uid, sid):
    try:
        if len(client.containers.list(all=True, filters={'name': uid + "-" + sid})) != 0:
            container = client.containers.get(uid + "-" + sid)
            port = container.ports['443/tcp'][0]['HostPort']
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("127.0.0.1", int(port)))
            sock.shutdown(2)
            if result == 0:
                response = requests.get("https://127.0.0.1:" + str(port), verify=False)
                if response.status_code == 200 or response.status_code == 401:
                    return {'status': "started", "port": port}
            return {'status': "processing", "port": port}
        else:
            return {'status': "none"}
    except:
        pass
    return {'status': "processing"}


def get_all_container_status(uid):
    rc = {"result": False, "ide": []}
    container_list = client.containers.list(all=True, filters={'name': uid + "-"})
    if len(container_list) != 0:
        for c in container_list:
            sID = c.name[len(uid + "-"):]
            port = c.ports['443/tcp'][0]['HostPort']
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("127.0.0.1", int(port)))
            if result == 0:
                try:
                    response = requests.get("https://127.0.0.1:" + str(port), verify=False)
                    if response.status_code == 200 or response.status_code == 401:
                        rc["ide"].append({"sID": sID, "status": "started", "port": port})
                        continue
                except:
                    pass
            rc["ide"].append({"sID": sID, "status": "starting", "port": port})
    rc["result"] = True
    return rc


def stop_container_thread(uid, sid):
    container = client.containers.get(uid + "-" + sid)
    while True:
        if container.status == "running":
            break
        time.sleep(0.5)
    port = container.ports['443/tcp'][0]['HostPort']
    container.stop(
        timeout=1
    )
    try:
        port = int(port)
        if (60000 <= port <= 60099) or (63000 <= port <= 63099):
            Ports.release_port(port)
    except ValueError:
        pass


def remove_container(uid, sid):
    if len(client.containers.list(all=True, filters={'name': uid + "-" + sid})) != 0:
        t = threading.Thread(target = stop_container_thread, args = (uid, sid))
        t.start()
        return "stopping"
    else:
        return "container not found"


def cleanup_volume(uid, sid):
    remove_container(uid, sid)
    app = current_app._get_current_object()
    src_path = app.config['STORAGE_POOL'] + '/strategies/' + uid + '/' + sid
    theia_config_path = app.config['STORAGE_POOL'] + '/theia_config/' + uid + '/' + sid
    shutil.rmtree(src_path, ignore_errors = True)
    shutil.rmtree(theia_config_path, ignore_errors = True)
    return ""
