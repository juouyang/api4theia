from flask import jsonify, abort, make_response, current_app, request
from . import main, auth
from app.models import users, strategies, save_user, save_strategy
import shortuuid
from urllib.parse import unquote
from ..docker import *

@main.route('/api/v1.0/users', methods=['GET'])
@auth.login_required(role='Admin')
def get_all_users():
    """Get all users by admin, return 200 or 401

    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/users

    """
    return jsonify({'users': users})


@main.route('/api/v1.0/strategies', methods=['GET'])
@auth.login_required()
def get_strategies():
    """Get all strategies of one user, return 200 or 401

    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategies

    """
    username = auth.current_user()
    user = [u for u in users if u['username'] == username]
    sid_list = user[0]['strategies']
    strategy_list = [s for s in strategies if str(s['sid']) in sid_list]
    return jsonify({'strategies': strategy_list})


@main.route('/api/v1.0/strategy/<sid>', methods=['GET'])
@auth.login_required()
def get_strategy(sid):
    """Get one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategy/${SID}

    """
    username = auth.current_user()
    user = [u for u in users if u['username'] == username]
    strategy_list = [s for s in strategies if s['sid'] == sid]
    if len(strategy_list) == 1 and sid in user[0]['strategies']:
        return jsonify({"strategy": strategy_list[0]})
    abort(404)


@main.route('/api/v1.0/strategy/<sid>/<key>', methods=['GET'])
@auth.login_required()
def get_strategy_field(sid, key):
    """Get one field of one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -k https://127.0.0.1:5000/api/v1.0/strategy/${SID}/${KEY}

    """
    username = auth.current_user()
    user = [u for u in users if u['username'] == username]
    strategy_list = [s for s in strategies if s['sid'] == sid]
    if len(strategy_list) == 1 and sid in user[0]['strategies'] and key in strategy_list[0].keys():
        return jsonify({key: strategy_list[0][key]})
    abort(404)


@main.route('/api/v1.0/strategies', methods=['POST'])
@auth.login_required()
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
    port = strategies[-1]['port'] + 1 if len(strategies) > 0 else app.config['CONTAINER_PORT']
    sid = shortuuid.uuid()

    username = auth.current_user()
    user = [u for u in users if u['username'] == username]
    if len(user[0]['strategies']) >= app.config['MAX_STRATEGY_NUM']:
        abort(make_response(jsonify(
            error="the service has reached its maximum number of strategy for user = "+username), 429))

    user[0]['strategies'].append(sid)
    save_user()
    strategy = {
        'sid': sid,
        'name': unquote(request.json['name']),
        'port': port,
        'url': u'https://' + app.config['FQDN'] + ':' + str(port),
        'theia': "not running",
        'uid': user[0]['uid']
    }
    strategies.append(strategy)
    save_strategy()
    return jsonify({'strategy': strategy}), 201


@main.route('/api/v1.0/strategies/<sid>', methods=['DELETE'])
@auth.login_required()
def delete_strategy(sid):
    """Delete one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -i -H "Content-Type: application/json" -X DELETE -k https://127.0.0.1:5000/api/v1.0/strategies/${NEW_SID}

    """
    username = auth.current_user()
    user = [u for u in users if u['username'] == username]
    if not len(user) == 1 or not sid in user[0]['strategies']:
        abort(404)
    u = user[0]
    uid = u['uid']
    cleanup_volume(uid, sid)
    strategy = list(filter(lambda t: str(t['sid']) == str(sid), strategies))
    if len(strategy) == 0:
        abort(404)
    strategies.remove(strategy[0])
    save_strategy()
    u['strategies'].remove(sid)
    save_user()
    return jsonify({'result': True})


@main.route('/api/v1.0/strategy/<sid>', methods=['PUT'])
@auth.login_required()
def update_strategy(sid):
    """Change fields of one strategy, return 200, 401 or 404

    $ curl -u admin:85114481 -i -H "Content-Type: application/json" -X PUT -d '{"name":"my_strategy_1"}' -k https://127.0.0.1:5000/api/v1.0/strategy/${SID}

    """
    username = auth.current_user()
    user = [u for u in users if u['username'] == username]
    if (not sid in user[0]['strategies']):
        abort(404)

    strategy_list = [s for s in strategies if s['sid'] == sid]
    if len(strategy_list) == 0:
        abort(404)
    if not request.json and 'name' in request.json and type(request.json['name']) != str:
        abort(400)
    s = strategy_list[0]
    new_name = request.json.get('name', s['name'])
    s['name'] = unquote(new_name)
    save_strategy()
    return jsonify({'strategy': s})


@main.route('/api/v1.0/strategy/<sid>/start', methods=['PUT'])
@auth.login_required()
def start_ide(sid):
    """Star IDE for one strategy, return 200, 401, 404, 429 or 500

    $ curl -u admin:85114481 -i -X PUT -k https://127.0.0.1:5000/api/v1.0/strategy/${SID}/start

    """
    app = current_app._get_current_object()
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
    if (len(running_theia_of_user) >= app.config['MAX_CONTAINER_NUM']):
        abort(make_response(jsonify(
            error="the service has reached its maximum number of container for user = "+username), 429))

    rc = run_container(uid, s['sid'], s['port'])
    if (rc == ""):
        s['theia'] = "running"
        return jsonify(s)
    if (rc == "docker.errors.ImageNotFound"):
        return rc, 404
    return rc, 500


@main.route('/api/v1.0/strategy/<sid>/stop', methods=['PUT'])
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