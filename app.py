#!venv/bin/python
from flask import Flask, g, abort, current_app, request, url_for, jsonify, make_response, render_template

from flask_httpauth import HTTPBasicAuth
from flask_selfdoc import Autodoc
from flask_restful import Resource, Api
from flask_cors import CORS

from werkzeug.exceptions import HTTPException, InternalServerError

from datetime import datetime
from functools import wraps
from urllib.parse import unquote

import json
import shortuuid
import docker
import os
import logging
import subprocess as sp
import threading
import time
import re

app = Flask(__name__)
app.config.from_pyfile('default_settings.py')

logging.getLogger('werkzeug').setLevel(app.config['LOG_LEVEL'])

cors = CORS(app)
auto = Autodoc(app)
api = Api(app)

client = docker.from_env()

with open('data/users.json') as f:
    users = json.load(f)

with open('data/strategies.json') as f:
    strategies = json.load(f)


def run_container(uid, sid, sname, port):
    if (len(client.images.list(name=app.config['DOCKER_IMAGE'])) == 0):
        return "docker.errors.ImageNotFound"

    src_template = app.config['STRATEGY_TEMPLATE']
    src_path = app.config['THEIA_ROOT'] + '/' + uid + '/' + sid + '/src'
    if not os.path.isdir(src_path):
        os.makedirs(src_path, exist_ok=True)
        if os.path.isdir(src_template):
            sp.call("cp -rf " + src_template + "/* " + src_path, shell=True)
            sp.call("mv -f " + src_path + '/Your_Strategy.py \"' + src_path + '/' + sname + '.py\"', shell=True)
        with open(src_path + "/.gitignore", "w") as out:
            out.write(app.config['GIT_IGNORE'])
        os.makedirs(src_path + '/.sandbox', exist_ok=True)
        with open(src_path + '/.sandbox/01_matplotlib_example.py', "w") as out:
            out.write(app.config['MATPLOTLIB_SAMPLE'])
        with open(src_path + '/.sandbox/02_ploty_candlestick.py', "w") as out:
            out.write(app.config['PLOTLY_SAMPLE'])
        sp.call("cd " + src_path + ";" + app.config['GIT_INIT'], shell=True)
    else:
        if os.path.isdir(src_template):
            sp.call("cp -rf " + src_template + "/reference/ " + src_path, shell=True)
            sp.call("cp -rf " + src_template + "/__main__.py " + src_path, shell=True)

    theia_config_path = app.config['THEIA_ROOT'] + '/' + uid + '/' + sid + '/theia_config'
    if not os.path.isdir(theia_config_path):
        os.makedirs(theia_config_path, exist_ok=True)

    if len(client.containers.list(all=True, filters={'name': sid})) == 0:
        try:
            client.containers.run(
                app.config['DOCKER_IMAGE'],
                auto_remove=True,
                detach=True,
                name=sid,
                ports={'443/tcp': port},
                volumes={
                    src_path + '/': {'bind': '/home/project/', 'mode': 'rw'},
                    theia_config_path + '/': {'bind': '/home/theia/.theia', 'mode': 'rw'}
                },
                mem_limit="1g",
                privileged=False
            )
            return ""
        except :
            return "error when start container"


def remove_container(sid):
    try:
        if len(client.containers.list(all=True, filters={'name': sid})) != 0:
            container = client.containers.get(sid)
            container.stop(
                timeout=0
            )
            if len(client.containers.list(all=True, filters={'name': sid})) != 0:
                container.remove()
    except:
        app.logger.error("exception while stopping container")


def cleanup_volume(uid, sid):
    folderpath = app.config['THEIA_ROOT'] + '/' + uid + '/' + sid
    remove_container(sid)
    sp.call("rm -rf " + folderpath, shell=True)


# authentication


auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    user = list(filter(lambda t: str(t['username']) == str(username), users))
    if len(user) == 0:
        return None
    return user[0]['password']


@auth.get_user_roles
def get_basic_role(username):
    user = list(filter(lambda t: str(t['username']) == str(username), users))
    if user[0]['is_admin']:
        return ['Admin']


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# backend


@app.route('/api/v1.0/users', methods=['GET'])
@auto.doc()
@auth.login_required(role='Admin')
def get_all_users():
    """Get all users by admin, return 200 or 401

    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/users
    200
    $ curl -u user1:85114481 -k https://127.0.0.1:5000/api/v1.0/users
    401

    """
    return jsonify({'users': users})
    # username_list = [temp_dict['username'] for temp_dict in users]
    # return jsonify({'users': username_list})


@app.route('/api/v1.0/strategies', methods=['GET'])
@auto.doc()
@auth.login_required()
def get_strategies():
    """Get all strategies of one user, return 200 or 401

    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategies
    200
    $ curl -u user1:85114481 -k https://127.0.0.1:5000/api/v1.0/strategies
    200
    $ curl -u foo:bar -k https://127.0.0.1:5000/api/v1.0/strategies
    401
    $ curl -k https://127.0.0.1:5000/api/v1.0/strategies
    401

    """
    username = auth.current_user()
    user_list = list(filter(lambda t: str(
        t['username']) == str(username), users))
    sid_list = user_list[0]['strategies']
    strategy_list = list(
        filter(lambda t: str(t['sid']) in sid_list, strategies))
    return jsonify({'strategies': strategy_list})


@app.route('/api/v1.0/strategy/<sid>', methods=['GET'])
@auto.doc()
@auth.login_required()
def get_strategy(sid):
    """Get one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV
    200
    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW
    404

    """
    username = auth.current_user()
    user = list(filter(lambda t: str(t['username']) == str(username), users))
    sid_list = user[0]['strategies']
    strategy_list = list(filter(lambda t: str(
        t['sid']) == sid and str(t['sid']) in sid_list, strategies))
    if len(strategy_list) > 0:
        return jsonify({"strategy": strategy_list[0]})
    abort(404)


@app.route('/api/v1.0/strategy/<sid>/<key>', methods=['GET'])
@auto.doc()
@auth.login_required()
def get_strategy_field(sid, key):
    """Get one field of one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/url
    200
    $ curl --u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/name
    200
    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/foobar
    404

    """
    username = auth.current_user()
    user = list(filter(lambda t: str(t['username']) == str(username), users))
    sid_list = user[0]['strategies']
    strategy_list = list(filter(lambda t: str(
        t['sid']) == sid and str(t['sid']) in sid_list, strategies))
    if len(strategy_list) > 0 and key in strategy_list[0].keys():
        return jsonify({key: strategy_list[0][key]})
    abort(404)


@app.route('/api/v1.0/strategies', methods=['POST'])
@auto.doc()
@auth.login_required()
def create_strategy():
    """Create a new strategy, return 201, 400, 401 or 429

    $ NEW_SID=$(curl -u admin:85114481 -sq -H "Content-Type: application/json" -X POST -d '{"name":"my_strategy_c"}' -k https://127.0.0.1:5000/api/v1.0/strategies | jq -r '.strategy.sid')
    201
    $ curl -u admin:85114481 -i -H "Content-Type: application/json" -X POST -d '{"name":"my_strategy_d"}' -k https://127.0.0.1:5000/api/v1.0/strategies
    429
    $ curl -u admin:85114481 -i -H "Content-Type: application/json" -X POST -d '{"foo":"bar"}' -k https://127.0.0.1:5000/api/v1.0/strategies
    400
    $ curl -u foo:bar -i -H "Content-Type: application/json" -X POST -d '{"name":"my_strategy_c"}' -k https://127.0.0.1:5000/api/v1.0/strategies
    401

    """
    if not request.json or not 'name' in request.json:
        abort(make_response(
            jsonify(error="the request should contain strategy name"), 400))

    # if not request.json or not 'sid' in request.json:
    #     abort(make_response(
    #         jsonify(error="the request should contain strategy ID"), 400))

    port = strategies[-1]['port'] + 1 if len(strategies) > 0 else app.config['THEIA_PORT']
    sid = shortuuid.uuid()

    username = auth.current_user()
    user = list(filter(lambda t: str(t['username']) == str(username), users))
    if len(user[0]['strategies']) >= app.config['MAX_STRATEGY_NUM']:
        abort(make_response(jsonify(
            error="the service has reached its maximum number of strategy for user = "+username), 429))

    user[0]['strategies'].append(sid)
    with open('data/users.json', 'w') as f:
        json.dump(users, f)
    strategy = {
        'sid': sid,
        'name': unquote(request.json['name']),
        'port': port,
        'url': u'https://' + app.config['DOCKER_HOST'] + ':' + str(port),
        'theia': "not running",
        'uid': user[0]['uid']
    }
    strategies.append(strategy)
    with open('data/strategies.json', 'w') as f:
        json.dump(strategies, f)
    return jsonify({'strategy': strategy}), 201


@app.route('/api/v1.0/strategies/<sid>', methods=['DELETE'])
@auto.doc()
@auth.login_required()
def delete_strategy(sid):
    """Delete one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -i -H "Content-Type: application/json" -X DELETE -k https://127.0.0.1:5000/api/v1.0/strategies/${NEW_SID}
    200
    $ curl -u foo:bar -i -H "Content-Type: application/json" -X DELETE -k https://127.0.0.1:5000/api/v1.0/strategies/${NEW_SID}
    401
    $ curl -u admin:85114481 -i -H "Content-Type: application/json" -X DELETE -k https://127.0.0.1:5000/api/v1.0/strategies/foobar
    404

    """
    username = auth.current_user()
    user = list(filter(lambda t: str(t['username']) == str(username), users))
    if not len(user) == 1 or not sid in user[0]['strategies']:
        abort(404)
    u = user[0]
    uid = u['uid']
    cleanup_volume(uid, sid)
    strategy = list(filter(lambda t: str(t['sid']) == str(sid), strategies))
    if len(strategy) == 0:
        abort(404)
    strategies.remove(strategy[0])
    with open('data/strategies.json', 'w') as f:
        json.dump(strategies, f)
    u['strategies'].remove(sid)
    with open('data/users.json', 'w') as f:
        json.dump(users, f)
    return jsonify({'result': True})


@app.route('/api/v1.0/strategy/<sid>', methods=['PUT'])
@auto.doc()
@auth.login_required()
def update_strategy(sid):
    """Change fields of one strategy, return 200, 401 or 404

    $ curl -u user1:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"name":"my_strategy_1"}' -k https://127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW
    200
    $ curl -u foo:bar -i -H "Content-Type: application/json" -X PUT -d '{"name":"my_strategy_1"}' -k https://127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW
    401
    $ curl -u user1:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"name":"my_strategy_1"}' -k https://127.0.0.1:5000/api/v1.0/strategy/foobar
    404
    """
    username = auth.current_user()
    user = list(filter(lambda t: str(t['username']) == str(username), users))
    if (not sid in user[0]['strategies']) and (user[0]['is_admin'] != True):
        abort(404)

    strategy = list(filter(lambda t: str(t['sid']) == str(sid), strategies))
    if len(strategy) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != str:
        abort(400)
    new_name = request.json.get('name', strategy[0]['name'])
    strategy[0]['name'] = unquote(new_name)
    with open('data/strategies.json', 'w') as f:
        json.dump(strategies, f)
    # change filename of strategy
    return jsonify({'strategy': strategy[0]})


@app.route('/api/v1.0/strategy/<sid>/start', methods=['PUT'])
@auto.doc()
@auth.login_required()
def start_ide(sid):
    """Star IDE for one strategy, return 200, 401, 404, 429 or 500

    $ curl -u admin:85114481 -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/start
    200
    $ curl -u foo:bar -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/start
    401
    $ curl -u admin:85114481 -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/foobar/start
    404

    """
    username = auth.current_user()
    user = list(filter(lambda t: str(t['username']) == str(username), users))
    if not sid in user[0]['strategies']:
        abort(404)

    strategy = list(filter(lambda t: str(t['sid']) == str(sid), strategies))
    if len(strategy) == 0:
        abort(404)
    s = strategy[0]

    user = list(filter(lambda t: str(sid) in str(t['strategies']), users))
    if len(strategy) == 0:
        abort(404)
    u = user[0]

    ## check running container, return 429 if more than limit
    uid = u['uid']
    running_theia_of_user = list(filter(lambda t: str(t['uid']) == str(uid) and t['theia'] == 'running', strategies))
    if (len(running_theia_of_user) >= app.config['RUNNING_THEIA_PER_USER']):
        abort(make_response(jsonify(
            error="the service has reached its maximum number of container for user = "+username), 429))

    rc = run_container(uid, s['sid'], s['name'], s['port'])
    if (rc == ""):
        s['theia'] = "running"
        return jsonify(s)
    if (rc == "docker.errors.ImageNotFound"):
        return rc, 404
    return rc, 500


@app.route('/api/v1.0/strategy/<sid>/stop', methods=['PUT'])
@auto.doc()
@auth.login_required()
def stop_ide(sid):
    """Stop IDE for one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/stop
    200
    $ curl -u foo:bar -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/stop
    401
    $ curl -u admin:85114481 -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/foobar/stop
    404

    """
    username = auth.current_user()
    user = list(filter(lambda t: str(t['username']) == str(username), users))
    if not sid in user[0]['strategies']:
        abort(404)

    strategy = list(filter(lambda t: str(t['sid']) == str(sid), strategies))
    if len(strategy) == 0:
        abort(404)

    s = strategy[0]
    remove_container(s['sid'])
    s['theia'] = "not running"
    return jsonify(s)


tasks = {}

def async_api(wrapped_function):
    @wraps(wrapped_function)
    def new_function(*args, **kwargs):
        def task_call(flask_app, environ):
            # Create a request context similar to that of the original request
            # so that the task can have access to flask.g, flask.request, etc.
            with flask_app.request_context(environ):
                try:
                    tasks[task_id]['return_value'] = wrapped_function(
                        *args, **kwargs)
                except HTTPException as e:
                    tasks[task_id]['return_value'] = current_app.handle_http_exception(
                        e)
                except Exception as e:
                    # The function raised an exception, so we set a 500 error
                    tasks[task_id]['return_value'] = InternalServerError()
                    if current_app.debug:
                        # We want to find out if something happened so reraise
                        raise
                finally:
                    # We record the time of the response, to help in garbage
                    # collecting old tasks
                    tasks[task_id]['completion_timestamp'] = datetime.timestamp(
                        datetime.utcnow())

                    # close the database session (if any)

        # Assign an id to the asynchronous task
        sid = kwargs['sid']
        task_id = sid

        # Record the task, and then launch it
        tasks[task_id] = {'task_thread': threading.Thread(
            target=task_call, args=(current_app._get_current_object(),
                                    request.environ))}
        tasks[task_id]['task_thread'].start()

        # Return a 202 response, with a link that the client can use to
        # obtain task status
        print(url_for('gettaskstatus', task_id=task_id))
        return url_for('gettaskstatus', task_id=task_id), 202, {'Location': url_for('gettaskstatus', task_id=task_id)}
    return new_function


class GetTaskStatus(Resource):
    @auth.login_required()
    def get(self, task_id):
        """
        Return status about an asynchronous task. If this request returns a 202
        status code, it means that task hasn't finished yet. Else, the response
        from the task is returned.
        """
        task = tasks.get(task_id)
        if task is None:
            abort(404)
        if 'return_value' not in task:
            return 'building docker image in the background ...', 202, {'Location': url_for('gettaskstatus', task_id=task_id)}
        return task['return_value']


class BuildDocker(Resource):
    @auth.login_required()
    @async_api
    def get(self, sid=''):
        # perform some intensive processing
        print("starting processing task, sid: '%s'" % sid)

        # user ID
        username = request.authorization['username']
        # strategy ID = sid
        path = username + "/" + sid + "/src"

        child = sp.Popen("cd /media/nfs/theia/" + path + "; " + app.config['PACK_CMD'], shell=True, stdout=sp.PIPE)
        #child = sp.Popen("cd /media/nfs/theia/" + path + "; bash build.sh", shell=True, stdout=sp.PIPE)
        #child = sp.Popen("echo foo; echo bar", shell=True, stdout=sp.PIPE)
        console_output = str(child.communicate()[0].decode()).strip()
        rc = child.returncode

        print("completed processing task with %d" % rc)

        list = console_output.split('\n')
        json = []
        for i in range(len(list)):
            json.append(list[i].replace('\r', ''))

        return json, 200 if rc == 0 else rc


# curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/build
api.add_resource(BuildDocker, '/api/v1.0/strategy/<sid>/build')
# curl -u admin:85114481 -k https://127.0.0.1:5000/status/YJMDUH9zuwXf8c6KT2CDEV
api.add_resource(GetTaskStatus, '/status/<task_id>')


# private


@app.before_first_request
def before_first_request():
    """Start a background thread that cleans up old tasks."""
    def clean_old_tasks():
        """
        This function cleans up old tasks from our in-memory data structure.
        """
        global tasks
        while True:
            # Only keep tasks that are running or that finished less than 5
            # minutes ago.
            five_min_ago = datetime.timestamp(datetime.utcnow()) - 5 * 60
            tasks = {task_id: task for task_id, task in tasks.items()
                     if 'completion_timestamp' not in task or task['completion_timestamp'] > five_min_ago}
            time.sleep(60)

    if not current_app.config['TESTING']:
        thread = threading.Thread(target=clean_old_tasks)
        thread.start()


# frontend


@app.route('/users', methods=['GET'])
@auth.login_required(role='Admin')
def get_all_users_html():
    return render_template('users.html', users=users)
    # username_list = [temp_dict['username'] for temp_dict in users]
    # return render_template('users.html', users=username_list)


@app.route('/strategies', methods=['GET'])
@auth.login_required()
def get_strategies_html():
    username = auth.current_user()
    user = list(filter(lambda t: str(t['username']) == str(username), users))
    sid_list = user[0]['strategies']
    strategy_list = list(
        filter(lambda t: str(t['sid']) in sid_list, strategies))
    g.user = user[0]
    return render_template('strategies.html', strategies=strategy_list)


@app.route('/doc')
def documentation():
    return auto.html()


if __name__ == '__main__':
    def sync_containers_status():
        for strategy in strategies:
            strategy['theia'] = "not running"
            if len(client.containers.list(all=True, filters={'name': strategy['sid']})) == 1:
                strategy['theia'] = "running"
    thread = threading.Thread(target=sync_containers_status)
    thread.start()

    context = (app.config['CRT_FILE'], app.config['KEY_FILE'])
    app.run(host='0.0.0.0', port='5000', debug=app.config['DEBUG'], ssl_context=context)
