import json
from flask import current_app

#if (current_app.config['DB'] == 'Json'):
with open('migrations/users.json') as f:
    users = json.load(f)
with open('migrations/strategies.json') as f:
    strategies = json.load(f)

def save_user():
    if (current_app.config['DB'] == 'Json'):
        with open('migrations/users.json', 'w') as f:
            json.dump(users, f)

def save_strategy():
    if (current_app.config['DB'] == 'Json'):
        with open('migrations/strategies.json', 'w') as f:
            json.dump(strategies, f)