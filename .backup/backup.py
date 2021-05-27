#!venv/bin/python
from flask import Flask, g, abort, current_app, request, url_for, jsonify, make_response, render_template
from flask_restful import Resource, Api
from werkzeug.exceptions import HTTPException, InternalServerError
from datetime import datetime
from functools import wraps
from urllib.parse import unquote
import json
import subprocess as sp
import threading
import time

api = Api(app)

# backend

@app.route('/api/v1.0/strategy/<sid>/start', methods=['PUT'])
@auto.doc()
@auth.login_required()
def start_ide(sid):
    """Star IDE for one strategy, return 200, 401, 404, 429 or 500

    $ curl -u admin:85114481 -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/${SID}/start

    """
    username = auth.current_user()
    user = [u for u in users if u['username'] == username]
    if not sid in user[0]['strategies']:
        abort(404)

    strategy_list = [s for s in strategies if s['sid'] == sid]
    if len(strategy_list) == 0:
        abort(404)
    s = strategy_list[0]

    user = [u for u in users if sid in u['strategies']]
    u = user[0]

    ## check running container, return 429 if more than limit
    uid = u['uid']
    running_theia_of_user = list(filter(lambda t: str(t['uid']) == str(uid) and t['theia'] == 'running', strategies))
    if (len(running_theia_of_user) >= app.config['RUNNING_THEIA_PER_USER']):
        abort(make_response(jsonify(
            error="the service has reached its maximum number of container for user = "+username), 429))

    rc = run_container(uid, s['sid'], s['port'])
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

    $ curl -u admin:85114481 -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/${SID}/stop

    """
    username = auth.current_user()
    user = [u for u in users if u['username'] == username]
    if not sid in user[0]['strategies']:
        abort(404)

    strategy_list = [s for s in strategies if s['sid'] == sid]
    if len(strategy_list) == 0:
        abort(404)

    s = strategy_list[0]
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

class PackImage(Resource):
    @auth.login_required()
    @async_api
    def get(self, sid=''):
        # perform some intensive processing
        print("starting processing task, sid: '%s'" % sid)

        # user ID
        username = request.authorization['username']
        uids = [u['uid'] for u in users if u['username'] == username and sid in u['strategies']]
        if not len(uids) == 1:
            abort(404)
        path = uids[0] + "/" + sid + "/src"

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

# curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/pack
api.add_resource(PackImage, '/api/v1.0/strategy/<sid>/pack')
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
