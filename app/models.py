import json
from flask import current_app

class Users:
    users = []

class Strategies:
    strategies = []

class Ports:
    available_ports = []

def init_data(app):
    if (app.config['TESTING']):
        Users.users = json.loads('''[{"is_admin": true, "password": "85114481", "strategies": [], "uid": "a001", "username": "admin"}, {"is_admin": false, "password": "85114481", "strategies": [], "uid": "u001", "username": "juice"}]''')
        Strategies.strategies = []
        Ports.available_ports = [60000,60001,60002,60003,60004,60005,60006,60007,60008,60009,60010,60011,60012,60013,60014,60015,60016,60017,60018,60019,60020,60021,60022,60023,60024,60025,60026,60027,60028,60029,60030,60031,60032,60033,60034,60035,60036,60037,60038,60039,60040,60041,60042,60043,60044,60045,60046,60047,60048,60049,60050,60051,60052,60053,60054,60055,60056,60057,60058,60059,60060,60061,60062,60063,60064,60065,60066,60067,60068,60069,60070,60071,60072,60073,60074,60075,60076,60077,60078,60079,60080,60081,60082,60083,60084,60085,60086,60087,60088,60089,60090,60091,60092,60093,60094,60095,60096,60097,60098,60099]
    else:
        with open('migrations/users.json') as f:
            Users.users = json.load(f)
        with open('migrations/strategies.json') as f:
            Strategies.strategies = json.load(f)
        with open('migrations/ports.json') as f:
            Ports.available_ports = json.load(f)

def save_users():
    if (current_app.config['DB'] == 'Json'):
        with open('migrations/users.json', 'w') as f:
            json.dump(Users.users, f)

def save_strategies():
    if (current_app.config['DB'] == 'Json'):
        with open('migrations/strategies.json', 'w') as f:
            json.dump(Strategies.strategies, f)

def save_ports():
    if (current_app.config['DB'] == 'Json'):
        with open('migrations/ports.json', 'w') as f:
            json.dump(Ports.available_ports, f)