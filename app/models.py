import json
from flask import current_app

class Users:
    users = []

class Strategies:
    strategies = []

def init_data(app):
    if (app.config['TESTING']):
        Users.users = json.loads('''[{"is_admin": true, "password": "85114481", "strategies": [], "uid": "a001", "username": "admin"}, {"is_admin": false, "password": "85114481", "strategies": [], "uid": "u001", "username": "juice"}]''')
        Strategies.strategies = []
    else:
        with open('migrations/users.json') as f:
            Users.users = json.load(f)
        with open('migrations/strategies.json') as f:
            Strategies.strategies = json.load(f)

def save_user():
    if (current_app.config['DB'] == 'Json'):
        with open('migrations/users.json', 'w') as f:
            json.dump(Users.users, f)

def save_strategy():
    if (current_app.config['DB'] == 'Json'):
        with open('migrations/strategies.json', 'w') as f:
            json.dump(Strategies.strategies, f)