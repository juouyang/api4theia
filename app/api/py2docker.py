from flask_restful import Resource
from flask import url_for, abort, current_app, request
from app.models import Users
from ..auth import basic
from werkzeug.exceptions import HTTPException, InternalServerError
from functools import wraps
from datetime import datetime
import threading
import subprocess as sp

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
    @basic.auth.login_required()
    @async_api
    def get(self, sid=''):
        # perform some intensive processing
        print("starting processing task, sid: '%s'" % sid)

        # user ID
        username = request.authorization['username']
        uids = [u['uid'] for u in Users.users if u['username'] == username and sid in u['strategies']]
        if not len(uids) == 1:
            abort(404)
        path = uids[0] + "/" + sid + "/src"

        app = current_app._get_current_object()
        child = sp.Popen("cd /media/nfs/theia/" + path + "; " + app.config['PACK_CMD'], shell=True, stdout=sp.PIPE)
        # child = sp.Popen("cd /media/nfs/theia/" + path + "; bash build.sh", shell=True, stdout=sp.PIPE)
        # child = sp.Popen("echo foo; echo bar", shell=True, stdout=sp.PIPE)
        console_output = str(child.communicate()[0].decode()).strip()
        rc = child.returncode

        print("completed processing task with %d" % rc)

        list = console_output.split('\n')
        json = []
        for i in range(len(list)):
            json.append(list[i].replace('\r', ''))

        return json, 200 if rc == 0 else rc
