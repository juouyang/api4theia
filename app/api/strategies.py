from flask import jsonify, abort, make_response, current_app, request
from . import api
from ..auth import basic
from app.models import Users, save_users, Strategies, save_strategies, Ports, save_ports
import shortuuid
from urllib.parse import unquote
from ..docker import *
import random

@api.route('/users', methods=['GET'])
@basic.auth.login_required(role='Admin')
def get_all_users():
    """Get all users by admin, return 200 or 401

    $ curl -u admin:85114481 -H "API_TOKEN: 85114481" -k https://127.0.0.1:5000/api/v1.0/users

    """
    API_TOKEN = request.headers.get('API_TOKEN')
    if (API_TOKEN == "85114481"):
        return jsonify({'users': Users.users})
    else:
        abort(404)


@api.route('/strategies', methods=['GET'])
@basic.auth.login_required()
def get_strategies():
    """Get all strategies of one user, return 200 or 401

    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategies

    """
    username = basic.auth.current_user()
    user = [u for u in Users.users if u['username'] == username]
    sid_list = user[0]['strategies']
    strategy_list = [s for s in Strategies.strategies if str(s['sid']) in sid_list]
    return jsonify({'strategies': strategy_list})


@api.route('/strategy/<sid>', methods=['GET'])
@basic.auth.login_required()
def get_strategy(sid):
    """Get one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategy/${SID}

    """
    username = basic.auth.current_user()
    user = [u for u in Users.users if u['username'] == username]
    strategy_list = [s for s in Strategies.strategies if s['sid'] == sid]
    if len(strategy_list) == 1 and sid in user[0]['strategies']:
        return jsonify({"strategy": strategy_list[0]})
    abort(404)


@api.route('/strategy/<sid>/<key>', methods=['GET'])
@basic.auth.login_required()
def get_strategy_field(sid, key):
    """Get one field of one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategy/${SID}/${KEY}

    """
    username = basic.auth.current_user()
    user = [u for u in Users.users if u['username'] == username]
    strategy_list = [s for s in Strategies.strategies if s['sid'] == sid]
    if len(strategy_list) == 1 and sid in user[0]['strategies'] and key in strategy_list[0].keys():
        return jsonify({key: strategy_list[0][key]})
    abort(404)


@api.route('/strategies', methods=['POST'])
@basic.auth.login_required()
def create_strategy():
    """Create a new strategy, return 201, 400, 401 or 429

    $ NEW_SID=$(curl -u admin:85114481 -sq -H "Content-Type: application/json" -X POST -d '{"name":"my_strategy_name"}' -k https://127.0.0.1:5000/api/v1.0/strategies | jq -r '.strategy.sid')

    """
    if not request.json or not 'name' in request.json:
        abort(make_response(
            jsonify(error="the request should contain strategy name"), 400))

    # if not request.json or not 'sid' in request.json:
    #     abort(make_response(
    #         jsonify(error="the request should contain strategy ID"), 400))

    app = current_app._get_current_object()
    port = Strategies.strategies[-1]['port'] + 1 if len(Strategies.strategies) > 0 else app.config['CONTAINER_PORT']
    sid = shortuuid.uuid()

    username = basic.auth.current_user()
    user = [u for u in Users.users if u['username'] == username]
    if len(user[0]['strategies']) >= app.config['MAX_STRATEGY_NUM']:
        abort(make_response(jsonify(
            error="the service has reached its maximum number of strategy for user = "+username), 429))

    user[0]['strategies'].append(sid)
    save_users()
    strategy = {
        'sid': sid,
        'name': unquote(request.json['name']),
        'port': port,
        'url': u'https://' + app.config['FQDN'] + ':' + str(port),
        'theia': "not running",
        'uid': user[0]['uid']
    }
    Strategies.strategies.append(strategy)
    save_strategies()
    return jsonify({'strategy': strategy}), 201


@api.route('/strategies/<sid>', methods=['DELETE'])
@basic.auth.login_required()
def delete_strategy(sid):
    """Delete one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -i -X DELETE -k https://127.0.0.1:5000/api/v1.0/strategies/${NEW_SID}

    """
    username = basic.auth.current_user()
    user = [u for u in Users.users if u['username'] == username]
    if not len(user) == 1 or not sid in user[0]['strategies']:
        abort(404)
    u = user[0]
    uid = u['uid']
    cleanup_volume(uid, sid)
    strategy = list(filter(lambda t: str(t['sid']) == str(sid), Strategies.strategies))
    if len(strategy) == 0:
        abort(404)
    Strategies.strategies.remove(strategy[0])
    save_strategies()
    u['strategies'].remove(sid)
    save_users()
    return jsonify({'result': True})


@api.route('/strategy/<sid>', methods=['PUT'])
@basic.auth.login_required()
def update_strategy(sid):
    """Change fields of one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"name":"my_strategy_1"}' -k https://127.0.0.1:5000/api/v1.0/strategy/${SID}

    """
    username = basic.auth.current_user()
    user = [u for u in Users.users if u['username'] == username]
    if (not sid in user[0]['strategies']):
        abort(404)

    strategy_list = [s for s in Strategies.strategies if s['sid'] == sid]
    if len(strategy_list) == 0:
        abort(404)
    if not request.json and 'name' in request.json and type(request.json['name']) != str:
        abort(400)
    s = strategy_list[0]
    new_name = request.json.get('name', s['name'])
    s['name'] = unquote(new_name)
    save_strategies()
    return jsonify({'strategy': s})


@api.route('/strategy/<sid>/start', methods=['PUT'])
def start_ide(sid):
    """Star IDE for one strategy, return 200, 304, 401, 404, 429 or 500

    $ curl -u admin:85114481 -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/${SID}/start

    """
    strategy_list = [s for s in Strategies.strategies if s['sid'] == sid]
    if len(strategy_list) == 0:
        abort(404)
    s = strategy_list[0]
    s['theia'] = "running"

    app = current_app._get_current_object()

    ## check running container, return 429 if more than limit
    uid = s['uid']
    running_theia_of_user = list(filter(lambda t: str(t['uid']) == str(uid) and t['theia'] == 'running', Strategies.strategies))
    if (len(running_theia_of_user) > app.config['MAX_CONTAINER_NUM']):
        s['theia'] = "not running"
        abort(make_response(jsonify(error="the service has reached its maximum number of container "), 429))

    rc = run_container(uid, s['sid'], s['port'])
    if (len(rc) == app.config['ONETIME_PW_LEN'] or rc == ""):
        s['theia'] = "running"
        return jsonify({'port': s['port'], 'onetime_pw': rc})
    s['theia'] = "not running"
    if (rc == "duplicate call"):
        return rc, 304
    if (rc == "docker.errors.ImageNotFound"):
        abort(make_response(jsonify(error=rc), 404))
    return rc, 500


@api.route('/strategy/<sid>/stop', methods=['PUT'])
def stop_ide(sid):
    """Stop IDE for one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/${SID}/stop

    """
    strategy_list = [s for s in Strategies.strategies if s['sid'] == sid]
    if len(strategy_list) == 0:
        abort(404)

    s = strategy_list[0]
    remove_container(s['uid'], s['sid'])
    s['theia'] = "not running"
    return jsonify(s)

# ================================================================================================

@api.route('/strategy/<uid>/<sid>/start', methods=['PUT'])
def start_ide_without_check(uid, sid):
    """Star IDE for one strategy, return 200, 304, 404 or 500

    $ curl -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/${USER_ID}/${STRATEGY_ID}/start

    """
    app = current_app._get_current_object()

    port = random.choice(Ports.available_ports)
    rc = run_container(uid, sid, port)
    if (len(rc) == app.config['ONETIME_PW_LEN'] or rc == ""):
        Ports.available_ports.remove(port)
        save_ports()
        return jsonify({'port': port, 'onetime_pw': rc})
    if (rc == "duplicate call"):
        return rc, 304
    if (rc == "docker.errors.ImageNotFound"):
        return rc, 404
    return rc, 500


@api.route('/strategy/<uid>/<sid>/stop', methods=['PUT'])
def stop_ide_without_check(uid, sid):
    """Stop IDE for one strategy, return 200, 404 or 500

    $ curl -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/${USER_ID}/${STRATEGY_ID}/stop

    """
    rc = remove_container(uid, sid)
    if (rc == "container not found"):
        return rc, 404
    try:
        port = int(rc)
        if 60000 <= port <= 60999:
            Ports.available_ports.append(port)
            save_ports()
            return jsonify({'result': True})
    except ValueError:
        return rc, 500
    return rc, 500


@api.route('/strategies/<uid>/<sid>', methods=['DELETE'])
def delete_strategy_without_check(uid, sid):
    """Delete one strategy, return 200 or 500

    $ curl -i -X DELETE -k https://127.0.0.1:5000/api/v1.0/strategies/${USER_ID}/${STRATEGY_ID}

    """
    rc = cleanup_volume(uid, sid)
    if (rc == ""):
        return jsonify({'result': True})
    return rc, 500