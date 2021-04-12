#!venv/bin/python
from flask import Flask, jsonify

app = Flask(__name__)

import docker, os
client = docker.from_env()
volume_root="/media/nfs/theia"

os.system("docker ps -a -q  --filter ancestor=theia-python:aicots")

def run_container(uuid, strategy_name, port):
    os.system("mkdir -p " + volume_root + '/' + uuid)
    os.system("tar -xf /root/builds/1_aicots/template/strategy-template.tar -C " + volume_root + '/' + uuid)
    os.system("mv -f " + volume_root + '/' + uuid + '/strategy-template.py ' + volume_root + '/' + uuid + '/' + strategy_name + '.py')
    client.containers.run(
        'theia-python:aicots',
        auto_remove=True,
        detach=True,
        name=uuid,
        ports={'3000/tcp': port},
        volumes={volume_root + '/' + uuid + '/': {'bind': '/home/project/', 'mode': 'rw'}}
    )

def stop_container(uuid):
    client.containers.stop(
        name=uuid
    )

containers = [
  {
    "port": 30000, 
    "name": "my_strategy_a",
    "status": "stop", 
    "url": "http://192.168.233.136:30000", 
    "uuid": "YJMDUH9zuwXf8c6KT2CDEV"
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

@app.route('/api/v1.0/containers/<uuid>', methods=['GET'])
def get_container(uuid):
    container = list(filter(lambda t: str(t['uuid']) == str(uuid), containers))
    if len(container) == 0:
        abort(404)
    return jsonify({'container': container[0]})

# curl -i -H "Content-Type: application/json" -X POST -d '{"name":"my_strategy_b"}' http://localhost:5000/api/v1.0/containers

from flask import request
#import uuid
import shortuuid

@app.route('/api/v1.0/containers', methods=['POST'])
def create_task():
    if not request.json or not 'name' in request.json:
        abort(400)
    port = containers[-1]['port'] + 1 if len(containers) > 0 else 30000
    container = {
        'uuid': shortuuid.uuid(),
        'name': request.json['name'],
        'port': port,
        'url': u'http://192.168.233.136:'+str(port),
        'status': "stop"
    }
    containers.append(container)
    return jsonify({'container': container}), 201

# curl -i -H "Content-Type: application/json" -X PUT -d '{"status":"start"}' http://localhost:5000/api/v1.0/containers/YJMDUH9zuwXf8c6KT2CDEV

@app.route('/api/v1.0/containers/<uuid>', methods=['PUT'])
def update_container(uuid):
    container = list(filter(lambda t: str(t['uuid']) == str(uuid), containers))
    if len(container) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != str:
        abort(400)
    if 'status' in request.json and type(request.json['status']) != str:
        abort(400)
    container[0]['name'] = request.json.get('name', container[0]['name'])
    container[0]['status'] = request.json.get('status', container[0]['status'])
    run_container(container[0]['uuid'], container[0]['name'], container[0]['port'])
    return jsonify({'container': container[0]})

# curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1.0/containers/<uuid>

@app.route('/api/v1.0/containers/<uuid>', methods=['DELETE'])
def delete_container(uuid):
    container = list(filter(lambda t: str(t['uuid']) == str(uuid), containers))
    if len(container) == 0:
        abort(404)
    stop_container(container[0]['uuid'])
    containers.remove(container[0])
    return jsonify({'result': True})

#

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)