import json
from flask import current_app
import random
import threading


class Users:
    users = []

    def save_users():
        if (current_app.config['DB'] == 'Json'):
            with open('migrations/users.json', 'w') as f:
                json.dump(Users.users, f)


class Strategies:
    strategies = []

    def save_strategies():
        if (current_app.config['DB'] == 'Json'):
            with open('migrations/strategies.json', 'w') as f:
                json.dump(Strategies.strategies, f)


lock = threading.Lock()

class Ports:
    available_ports = []

    def get_unused_port():
        port = -1
        with lock:
            if len(Ports.available_ports) != 0:
                port = random.choice(Ports.available_ports)
                Ports.available_ports.remove(port)
        return port

    def release_port(port):
        Ports.available_ports.append(port)

    def save_ports(): # function that no one called
        if (current_app.config['DB'] == 'Json'):
            with open('migrations/ports.json', 'w') as f:
                json.dump(Ports.available_ports, f)


def init_data(app):
    if (app.config['TESTING']):
        Users.users = json.loads(
            '''[{"is_admin": true, "password": "85114481", "strategies": [], "uid": "a001", "username": "admin"}, {"is_admin": false, "password": "85114481", "strategies": [], "uid": "u001", "username": "juice"}]''')
        Strategies.strategies = []
        Ports.available_ports = [63000, 63001, 63002, 63003, 63004, 63005, 63006, 63007, 63008, 63009, 63010, 63011, 63012, 63013, 63014, 63015, 63016, 63017, 63018, 63019, 63020, 63021, 63022, 63023, 63024, 63025, 63026, 63027, 63028, 63029, 63030, 63031, 63032, 63033, 63034, 63035, 63036, 63037, 63038, 63039, 63040, 63041, 63042, 63043, 63044, 63045, 63046, 63047,
                                 63048, 63049, 63050, 63051, 63052, 63053, 63054, 63055, 63056, 63057, 63058, 63059, 63060, 63061, 63062, 63063, 63064, 63065, 63066, 63067, 63068, 63069, 63070, 63071, 63072, 63073, 63074, 63075, 63076, 63077, 63078, 63079, 63080, 63081, 63082, 63083, 63084, 63085, 63086, 63087, 63088, 63089, 63090, 63091, 63092, 63093, 63094, 63095, 63096, 63097, 63098, 63099]
    else:
        with open('migrations/users.json') as f:
            Users.users = json.load(f)
        with open('migrations/strategies.json') as f:
            Strategies.strategies = json.load(f)
        with open('migrations/ports.json') as f:
            Ports.available_ports = json.load(f)
