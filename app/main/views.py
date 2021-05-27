from flask import render_template, g, current_app
from . import main
from ..auth import basic
from app.models import Users, Strategies

@main.route('/users', methods=['GET'])
@basic.auth.login_required(role='Admin')
def get_all_users_html():
    return render_template('users.html', users=Users.users)


@main.route('/', methods=['GET'])
@basic.auth.login_required()
def get_strategies_html():
    username = basic.auth.current_user()
    user = [u for u in Users.users if u['username'] == username]
    sid_list = user[0]['strategies']
    strategy_list = list(
        filter(lambda t: str(t['sid']) in sid_list, Strategies.strategies))
    g.user = user[0]
    return render_template('strategies.html', strategies=strategy_list)


@main.route('/doc')
def doc():
    app = current_app._get_current_object()
    return app.send_static_file('doc.html')