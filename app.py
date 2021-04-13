#!venv/bin/python
from flask import Flask, jsonify

app = Flask(__name__)

import docker, os

client = docker.from_env()
volume_root = "/media/nfs/theia"
service_image = "theia-python:aicots"
service_addr = "192.168.233.136"
service_port = 30000
template_dir = "/root/builds/1_aicots/template/0.1/Strategy"

# docker rm $(docker stop $(docker ps -a -q  --filter ancestor=theia-python:aicots))
for container in client.containers.list(all=True, filters={'ancestor': service_image}):
    try:
        cid = container.attrs.get(id)
        container.stop()
        if len(client.containers.list(all=True, filters={'id': cid})) != 0:
            container.remove()
    except docker.errors.APIError:
        app.logger.error("error when remove container")

def run_container(uid, sid, strategy_name, port):
    folderpath = volume_root + '/' + uid + '/' + sid
    if not os.path.isdir(folderpath):
        os.system("mkdir -p " + folderpath)
        if os.path.isdir(template_dir):
            os.system("cp -rf " + template_dir + "/* " + folderpath)
            os.system("mv -f " + folderpath + '/Your_Strategy.py ' + folderpath + '/' + strategy_name + '.py')
    else:
        os.system("cp -rf " + template_dir + "/reference/ " + folderpath)
        os.system("cp -rf " + template_dir + "/__main__.py " + folderpath)

    if len(client.containers.list(all=True, filters={'name': sid})) == 0:
        client.containers.run(
            service_image,
            auto_remove=True,
            detach=True,
            name=sid,
            ports={'3000/tcp': port},
            volumes={folderpath + '/': {'bind': '/home/project/', 'mode': 'rw'}}
        )

def remove_container(sid):
    try:
        if len(client.containers.list(all=True, filters={'name': sid})) != 0:
            container = client.containers.get(sid)
            container.stop()
            if len(client.containers.list(all=True, filters={'name': sid})) != 0:
                container.remove()
    except:
        app.logger.error("error when stop container")

def cleanup_volume(uid, sid):
    folderpath = volume_root + '/' + uid + '/' + sid
    remove_container(sid)
    os.system("rm -rf " + folderpath)

#

containers = [
  {
    "port": service_port, 
    "name": "my_strategy_a",
    "url": "http://" + service_addr + ":" + str(service_port), 
    "sid": "YJMDUH9zuwXf8c6KT2CDEV",
    "status": "not running"
  }
]

#

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'aicots':
        return '85114481'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

#

from flask import make_response

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# curl -u aicots:85114481 -i http://127.0.0.1:5000/api/v1.0/containers

@app.route('/api/v1.0/containers', methods=['GET'])
@auth.login_required
def get_containers():
    return jsonify({'containers': containers})

# curl -i http://localhost:5000/api/v1.0/containers/YJMDUH9zuwXf8c6KT2CDEV

from flask import abort

@app.route('/api/v1.0/containers/<sid>', methods=['GET'])
def get_container(sid):
    container = list(filter(lambda t: str(t['sid']) == str(sid), containers))
    if len(container) == 0:
        abort(404)
    return jsonify({'container': container[0]})

# curl -i -H "Content-Type: application/json" -X POST -d '{"name":"my_strategy_b"}' http://localhost:5000/api/v1.0/containers

from flask import request
import shortuuid

@app.route('/api/v1.0/containers', methods=['POST'])
def create_task():
    if not request.json or not 'name' in request.json:
        abort(400)
    port = containers[-1]['port'] + 1 if len(containers) > 0 else service_port
    container = {
        'sid': shortuuid.uuid(),
        'name': request.json['name'],
        'port': port,
        'url': u'http://' + service_addr + ':' + str(port),
        'status': "not running"
    }
    containers.append(container)
    return jsonify({'container': container}), 201

# curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"start"}' http://localhost:5000/api/v1.0/containers/YJMDUH9zuwXf8c6KT2CDEV
# curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"stop"}' http://localhost:5000/api/v1.0/containers/YJMDUH9zuwXf8c6KT2CDEV

@app.route('/api/v1.0/containers/<sid>', methods=['PUT'])
def update_container(sid):
    container = list(filter(lambda t: str(t['sid']) == str(sid), containers))
    if len(container) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != str:
        abort(400)
    if 'action' in request.json and type(request.json['action']) != str:
        abort(400)
    container[0]['name'] = request.json.get('name', container[0]['name'])

    if request.json['action'] == "start":
        run_container("aicots", container[0]['sid'], container[0]['name'], container[0]['port'])
        container[0]['status'] = "running"
    else:
        if request.json['action'] == "stop":
            remove_container(container[0]['sid'])
            container[0]['status'] = "not running"
    return jsonify({'container': container[0]})

# curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1.0/containers/<sid>

@app.route('/api/v1.0/containers/<sid>', methods=['DELETE'])
def delete_container(sid):
    cleanup_volume("aicots", sid)

    container = list(filter(lambda t: str(t['sid']) == str(sid), containers))
    if len(container) == 0:
        abort(404) 
    containers.remove(container[0])
    return jsonify({'result': True})

#

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)