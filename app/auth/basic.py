from flask import make_response, jsonify
from flask_httpauth import HTTPBasicAuth
from app.models import Users

auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    user = [u for u in Users.users if u['username'] == username]
    if len(user) == 0:
        return None
    return user[0]['password']

@auth.get_user_roles
def get_user_roles(username):
    user = [u for u in Users.users if u['username'] == username]
    if user[0]['is_admin']:
        return ['Admin']

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)