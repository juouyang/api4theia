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
        "uid": "admin",
        "password": "85114481",
        "is_admin": True,
        "strategies": [
            "YJMDUH9zuwXf8c6KT2CDEV",
            "oMTmLAhDhNAArmp8Go64Hu"
        ]
    },
    {
        "uid": "user1",
        "password": "85114481",
        "is_admin": False,
        "strategies": [
            "9JYN5ycAEfoVNTkFxFQQxW"
        ]
    }
]
strategies = [
    {
        "sid": "YJMDUH9zuwXf8c6KT2CDEV",
        "port": service_port,
        "name": "my_strategy_a",
        "url": "http://" + service_addr + ":" + str(service_port),
        
        "theia": "not running"
    },
    {
        "sid": "oMTmLAhDhNAArmp8Go64Hu",
        "port": service_port+1,
        "name": "my_strategy_b",
        "url": "http://" + service_addr + ":" + str(service_port+1),
        "theia": "not running"
    },
    {
        "sid": "9JYN5ycAEfoVNTkFxFQQxW",
        "port": service_port+2,
        "name": "my_strategy_a",
        "url": "http://" + service_addr + ":" + str(service_port+2),
        "theia": "not running"
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
    user = list(filter(lambda t: str(t['uid']) == str(username), users))
    if len(user) == 0:
        return None
    return user[0]['password']

@auth.get_user_roles
def get_basic_role(username):
    user = list(filter(lambda t: str(t['uid']) == str(username), users))
    if user[0]['is_admin']:
        return ['Admin']

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#

# curl -u admin:85114481 -i http://127.0.0.1:5000/api/v1.0/strategies/all
# curl -u user1:85114481 -i http://127.0.0.1:5000/api/v1.0/strategies/all
@app.route('/api/v1.0/strategies/all', methods=['GET'])
@auth.login_required(role='Admin')
def get_all_strategies():
    return jsonify({'strategies': strategies})

# curl -u admin:85114481 -i http://127.0.0.1:5000/api/v1.0/strategies
# curl -u user1:85114481 -i http://127.0.0.1:5000/api/v1.0/strategies
@app.route('/api/v1.0/strategies', methods=['GET'])
@auth.login_required()
def get_strategies():
    username = auth.current_user()
    user = list(filter(lambda t: str(t['uid']) == str(username), users))
    sid_list = user[0]['strategies']
    strategy_list = list(filter(lambda t: str(t['sid']) in sid_list, strategies))
    return jsonify({'strategies': strategy_list})

# curl -u admin:85114481 -i http://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/url
# curl -u admin:85114481 -i http://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/name
# curl -u user1:85114481 -i http://127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW/url
# curl -u user1:85114481 -i http://127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW/name
@app.route('/api/v1.0/strategy/<sid>', methods=['GET'])
@auth.login_required()
def get_strategy(sid):
    username = auth.current_user()
    app.logger.info(username)
    user = list(filter(lambda t: str(t['uid']) == str(username), users))
    sid_list = user[0]['strategies']
    strategy_list = list(filter(lambda t: str(t['sid']) == sid and str(t['sid']) in sid_list, strategies))
    if len(strategy_list) > 0:
        return jsonify({"strategy": strategy_list[0]})
    abort(404)

# curl -u admin:85114481 -i http://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/url
# curl -u admin:85114481 -i http://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/name
# curl -u user1:85114481 -i http://127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW/url
# curl -u user1:85114481 -i http://127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW/name
@app.route('/api/v1.0/strategy/<sid>/<key>', methods=['GET'])
@auth.login_required()
def get_strategy_field(sid, key):
    username = auth.current_user()
    app.logger.info(username)
    user = list(filter(lambda t: str(t['uid']) == str(username), users))
    sid_list = user[0]['strategies']
    strategy_list = list(filter(lambda t: str(t['sid']) == sid and str(t['sid']) in sid_list, strategies))
    if len(strategy_list) > 0 and key in strategy_list[0].keys():
        return jsonify({key: strategy_list[0][key]})
    abort(404)

# curl -u admin:85114481 -i -H "Content-Type: application/json" -X POST -d '{"name":"my_strategy_c"}' http://localhost:5000/api/v1.0/strategies
@app.route('/api/v1.0/strategies', methods=['POST'])
@auth.login_required()
def create_strategy():
    if not request.json or not 'name' in request.json:
        abort(make_response(jsonify(error="the request should contain strategy name"), 400))

    port = strategies[-1]['port'] + 1 if len(strategies) > 0 else service_port
    sid = shortuuid.uuid()

    username = auth.current_user()
    user = list(filter(lambda t: str(t['uid']) == str(username), users))
    if len(user[0]['strategies']) >= 3:
        abort(make_response(jsonify(error="the service has reached its maximum number of container instances for username = "+username), 429))

    user[0]['strategies'].append(sid)  
    strategy = {
        'sid': sid,
        'name': request.json['name'],
        'port': port,
        'url': u'http://' + service_addr + ':' + str(port),
        'theia': "not running"
    }
    strategies.append(strategy)
    return jsonify({'strategy': strategy}), 201

# curl -u admin:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"action":"start"}' http://localhost:5000/api/v1.0/strategies/YJMDUH9zuwXf8c6KT2CDEV
# curl -u user1:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"action":"start"}' http://localhost:5000/api/v1.0/strategies/YJMDUH9zuwXf8c6KT2CDEV
# curl -u user1:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"action":"stop"}' http://localhost:5000/api/v1.0/strategies/YJMDUH9zuwXf8c6KT2CDEV
# curl -u admin:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"action":"stop"}' http://localhost:5000/api/v1.0/strategies/YJMDUH9zuwXf8c6KT2CDEV
# curl -u user1:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"action":"start"}' http://localhost:5000/api/v1.0/strategies/9JYN5ycAEfoVNTkFxFQQxW
# curl -u admin:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"action":"stop"}' http://localhost:5000/api/v1.0/strategies/9JYN5ycAEfoVNTkFxFQQxW
# curl -u admin:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"action":"start"}' http://localhost:5000/api/v1.0/strategies/9JYN5ycAEfoVNTkFxFQQxW
# curl -u user1:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"action":"stop"}' http://localhost:5000/api/v1.0/strategies/9JYN5ycAEfoVNTkFxFQQxW
@app.route('/api/v1.0/strategies/<sid>', methods=['PUT'])
@auth.login_required()
def update_strategy(sid):
    uid = auth.current_user() 
    user = list(filter(lambda t: str(t['uid']) == str(uid), users))
    if (not sid in user[0]['strategies']) and (user[0]['is_admin'] != True):
        abort(404)

    strategy = list(filter(lambda t: str(t['sid']) == str(sid), strategies))
    if len(strategy) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != str:
        abort(400)
    if 'action' in request.json and type(request.json['action']) != str:
        abort(400)
    strategy[0]['name'] = request.json.get('name', strategy[0]['name'])

    real_user = list(filter(lambda t: str(sid) in str(t['strategies']), users))
    if request.json['action'] == "start":
        run_container(real_user[0]['uid'], strategy[0]['sid'], strategy[0]['name'], strategy[0]['port'])
        strategy[0]['theia'] = "running"
    elif request.json['action'] == "stop":
        remove_container(strategy[0]['sid'])
        strategy[0]['theia'] = "not running"
    return jsonify({'strategy': strategy[0]})

# curl -u user1:85114481 -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1.0/strategies/YJMDUH9zuwXf8c6KT2CDEV
# curl -u admin:85114481 -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1.0/strategies/YJMDUH9zuwXf8c6KT2CDEV
# curl -u admin:85114481 -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1.0/strategies/9JYN5ycAEfoVNTkFxFQQxW
# curl -u user1:85114481 -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1.0/strategies/9JYN5ycAEfoVNTkFxFQQxW
@app.route('/api/v1.0/strategies/<sid>', methods=['DELETE'])
@auth.login_required()
def delete_strategy(sid):
    uid = auth.current_user() 
    user = list(filter(lambda t: str(t['uid']) == str(uid), users))
    if not sid in user[0]['strategies']:
        abort(404)
    cleanup_volume(uid, sid)  
    strategy = list(filter(lambda t: str(t['sid']) == str(sid), strategies))
    if len(strategy) == 0:
        abort(404) 
    strategies.remove(strategy[0])
    user[0]['strategies'].remove(sid);
    return jsonify({'result': True})

#

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
