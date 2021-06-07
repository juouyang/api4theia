import unittest
from app import create_app
from base64 import b64encode
import random
import time
import socket
import requests
import subprocess as sp


class API4IDETestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_ide(self):
        sp.call("docker stop uid-000000-sid-000000", shell=True)

        response = self.client.get("/api/v1.0/strategy/uid-000000/sid-000000/status")
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        ide_status = resp_body['status']
        assert ide_status == "none"

        response = self.client.put("/api/v1.0/strategy/uid-000000/sid-000000/start")
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 202
        resp_body = response.json
        theia_port = resp_body['port']

        try:
            ide_status = "starting"
            while (True):
                response = self.client.get("/api/v1.0/strategy/uid-000000/sid-000000/status")
                if (response.status_code == 200):
                    resp_body = response.json
                    ide_status = resp_body['status']
                    break
            assert ide_status == "started"

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.app.config['FQDN'], int(theia_port)))
            assert result == 0

            while (True):
                response = requests.get("https://" + self.app.config['FQDN'] + ":" + str(theia_port), verify=False)
                if (response.status_code == 200):
                    break
                time.sleep(0.1)
        finally:
            response = self.client.put("/api/v1.0/strategy/uid-000000/sid-000000/stop")
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 200

        response = self.client.delete("/api/v1.0/strategies/uid-000000/sid-000000")
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200

    def test_multiple_start_ide_1(self):
        for i in range(9):
            uID = "uid-" + str(random.randrange(1, 30000)).zfill(6)
            sID = "sid-" + str(random.randrange(1, 30000)).zfill(6)
            response = self.client.put("/api/v1.0/strategy/" + uID + "/" + sID + "/start")
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 202
            resp_body = response.json

            ide_status = "starting"
            while (True):
                response = self.client.get("/api/v1.0/strategy/" + uID + "/" + sID + "/status")
                if (response.status_code == 200):
                    resp_body = response.json
                    ide_status = resp_body['status']
                    break
            assert ide_status == "started"

            response = self.client.put("/api/v1.0/strategy/" + uID + "/" + sID + "/stop")
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 200

            response = self.client.delete("/api/v1.0/strategies/" + uID + "/" + sID)
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 200

    def test_multiple_start_ide_2(self):
        for i in range(9):
            uID = "uid-" + str(random.randrange(30001, 60000)).zfill(6)
            sID = "sid-" + str(random.randrange(30001, 60000)).zfill(6)
            response = self.client.put("/api/v1.0/strategy/" + uID + "/" + sID + "/start")
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 202
            resp_body = response.json

            ide_status = "starting"
            while (True):
                response = self.client.get("/api/v1.0/strategy/" + uID + "/" + sID + "/status")
                if (response.status_code == 200):
                    resp_body = response.json
                    ide_status = resp_body['status']
                    break
            assert ide_status == "started"

            response = self.client.put("/api/v1.0/strategy/" + uID + "/" + sID + "/stop")
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 200

            response = self.client.delete("/api/v1.0/strategies/" + uID + "/" + sID)
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 200

    def test_multiple_start_ide_3(self):
        for i in range(9):
            uID = "uid-" + str(random.randrange(60001, 90000)).zfill(6)
            sID = "sid-" + str(random.randrange(60001, 90000)).zfill(6)
            response = self.client.put("/api/v1.0/strategy/" + uID + "/" + sID + "/start")
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 202
            resp_body = response.json

            ide_status = "starting"
            while (True):
                response = self.client.get("/api/v1.0/strategy/" + uID + "/" + sID + "/status")
                if (response.status_code == 200):
                    resp_body = response.json
                    ide_status = resp_body['status']
                    break
            assert ide_status == "started"

            response = self.client.put("/api/v1.0/strategy/" + uID + "/" + sID + "/stop")
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 200

            response = self.client.delete("/api/v1.0/strategies/" + uID + "/" + sID)
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 200