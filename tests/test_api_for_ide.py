import unittest
from app import create_app
from base64 import b64encode
import random
import time
import socket
import requests
import subprocess as sp
import threading

def job_start_stop_clean_ide(self, uID, sID):
    try:
        response = self.client.put("/api/v1.0/strategy/" + uID + "/" + sID + "/start")
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 202
        resp_body = response.json
        assert resp_body['message'] == ""
        theia_port = resp_body['port']

        while (True):
            response = self.client.get("/api/v1.0/strategy/" + uID + "/" + sID + "/status")
            if (response.status_code == 200):
                resp_body = response.json
                ide_status = resp_body['status']
                if (ide_status == "started"):
                    break

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((self.app.config['FQDN'], int(theia_port)))
        assert result == 0

        while (True):
            response = requests.get("https://" + self.app.config['FQDN'] + ":" + str(theia_port), verify=False)
            if (response.status_code == 200):
                break
            time.sleep(0.1)

        response = self.client.put("/api/v1.0/strategy/" + uID + "/" + sID + "/stop")
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 202

        while (True):
            response = self.client.get("/api/v1.0/strategy/" + uID + "/" + sID + "/status")
            if (response.status_code == 200):
                resp_body = response.json
                ide_status = resp_body['status']
                if (ide_status == "none"):
                    break
    except:
        raise Exception()
    finally:
        response = self.client.delete("/api/v1.0/strategies/" + uID + "/" + sID)
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200

class API4IDETestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_ide(self):
        sp.call("docker stop --time 1 $(docker ps -aq -f name=uid-000000-sid-000000)", shell=True)

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
            while (True):
                response = self.client.get("/api/v1.0/strategy/uid-000000/sid-000000/status")
                if (response.status_code == 200):
                    resp_body = response.json
                    ide_status = resp_body['status']
                    if ide_status == "started":
                        break

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
            assert response.status_code == 202
            while (True):
                response = self.client.get("/api/v1.0/strategy/uid-000000/sid-000000/status")
                if (response.status_code == 200):
                    resp_body = response.json
                    ide_status = resp_body['status']
                    if (ide_status == "none"):
                        break

        response = self.client.delete("/api/v1.0/strategies/uid-000000/sid-000000")
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200

    def test_multiple_start_ide_1(self):
        for i in range(33):
            uID = "uid-" + str(100000 + i).zfill(6)
            sID = "sid-" + str(100000 + i).zfill(6)
            t = threading.Thread(target = job_start_stop_clean_ide, args = (self, uID, sID))
            t.start()

    def test_multiple_start_ide_2(self):
        for i in range(33):
            uID = "uid-" + str(200000 + i).zfill(6)
            sID = "sid-" + str(200000 + i).zfill(6)
            t = threading.Thread(target = job_start_stop_clean_ide, args = (self, uID, sID))
            t.start()

    def test_multiple_start_ide_3(self):
        for i in range(33):
            uID = "uid-" + str(300000 + i).zfill(6)
            sID = "sid-" + str(300000 + i).zfill(6)
            t = threading.Thread(target = job_start_stop_clean_ide, args = (self, uID, sID))
            t.start()

    def test_get_all_ide_status(self):
        uID = "uid-999999"
        sp.call("docker stop $(docker ps -aq -f name=" + uID + ")", shell=True)

        for sID in ["sid-000001", "sid-000002", "sid-000003"]:
            response = self.client.put("/api/v1.0/strategy/" + uID + "/" + sID + "/start")
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 202

        response = self.client.get("/api/v1.0/strategies/" + uID + "/status")
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        assert resp_body["result"] == True
        assert len(resp_body["ide"]) == 3
        for i in resp_body["ide"]:
            assert 63000 <= int(i["port"]) <= 63099
            assert i["sID"] in ["sid-000001", "sid-000002", "sid-000003"]


        for sID in ["sid-000001", "sid-000002", "sid-000003"]:
            response = self.client.put("/api/v1.0/strategy/" + uID + "/" + sID + "/stop")
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 202

            while (True):
                response = self.client.get("/api/v1.0/strategy/" + uID + "/" + sID + "/status")
                if (response.status_code == 200):
                    resp_body = response.json
                    ide_status = resp_body['status']
                    if (ide_status == "none"):
                        break

            response = self.client.delete("/api/v1.0/strategies/" + uID + "/" + sID)
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 200