#!venv/bin/python
from flask import Flask, jsonify
from flask_httpauth import HTTPBasicAuth
from flask import make_response
from flask import abort
from flask import request
import shortuuid
import docker, os

app = Flask(__name__)

client = docker.from_env()
volume_root = "/media/nfs/theia"
template_dir = "/root/builds/1_aicots/template/0.1/Strategy"
service_image = "theia-python:aicots"
service_addr = "192.168.233.136"
service_port = 30000
users = [
    {
        "name": "admin",
        "password": "85114481",
        "is_admin": True,
        "strategies": [
            "YJMDUH9zuwXf8c6KT2CDEV",
            "oMTmLAhDhNAArmp8Go64Hu"
        ]
    },
    {
        "name": "user1",
        "password": "85114481",
        "is_admin": False,
        "strategies": [
            "9JYN5ycAEfoVNTkFxFQQxW"
        ]
    }
]
containers = [
    {
        "port": service_port,
        "name": "my_strategy_a",
        "url": "http://" + service_addr + ":" + str(service_port),
        "sid": "YJMDUH9zuwXf8c6KT2CDEV",
        "status": "not running"
    },
    {
        "port": service_port+1,
        "name": "my_strategy_b",
        "url": "http://" + service_addr + ":" + str(service_port),
        "sid": "oMTmLAhDhNAArmp8Go64Hu",
        "status": "not running"
    },
    {
        "port": service_port+2,
        "name": "my_strategy_a",
        "url": "http://" + service_addr + ":" + str(service_port),
        "sid": "9JYN5ycAEfoVNTkFxFQQxW",
        "status": "not running"
    }
]

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

auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    user = list(filter(lambda t: str(t['name']) == str(username), users))
    if len(user) == 0:
        return None
    return user[0]['password']

@auth.get_user_roles
def get_basic_role(username):
    user = list(filter(lambda t: str(t['name']) == str(username), users))
    if user[0]['is_admin']:
        return ['Admin']

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#

# curl -u admin:85114481 -i http://127.0.0.1:5000/api/v1.0/containers/all
# curl -u user1:85114481 -i http://127.0.0.1:5000/api/v1.0/containers/all
@app.route('/api/v1.0/containers/all', methods=['GET'])
@auth.login_required(role='Admin')
def get_all_containers():
    return jsonify({'containers': containers})

# curl -u admin:85114481 -i http://127.0.0.1:5000/api/v1.0/containers
# curl -u user1:85114481 -i http://127.0.0.1:5000/api/v1.0/containers
@app.route('/api/v1.0/containers', methods=['GET'])
@auth.login_required()
def get_strategies():
    username = auth.current_user()
    user = list(filter(lambda t: str(t['name']) == str(username), users))
    sid_list = user[0]['strategies']
    container_list = list(filter(lambda t: str(t['sid']) in sid_list, containers))
    return jsonify({'containers': container_list})

# curl -u admin:85114481 -i -H "Content-Type: application/json" -X POST -d '{"name":"my_strategy_c"}' http://localhost:5000/api/v1.0/containers
@app.route('/api/v1.0/containers', methods=['POST'])
@auth.login_required()
def create_strategy():
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
def update_strategy(sid):
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
def delete_strategy(sid):
    cleanup_volume("aicots", sid)

    container = list(filter(lambda t: str(t['sid']) == str(sid), containers))
    if len(container) == 0:
        abort(404) 
    containers.remove(container[0])
    return jsonify({'result': True})

#

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
