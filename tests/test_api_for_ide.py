import unittest
from app import create_app
from base64 import b64encode


class API4IDETestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_ide(self):
        response = self.client.put("/api/v1.0/strategy/uid-000000/sid-000000/start")
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 202
        resp_body = response.json
        theia_port = resp_body['port']
        print(theia_port)

        import time
        time.sleep(3)

        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((self.app.config['FQDN'], int(theia_port)))
        assert result == 0

        import requests
        response = requests.get(
            "https://" + self.app.config['FQDN'] + ":" + str(theia_port), verify=False)
        assert response.status_code == 200

        response = self.client.put("/api/v1.0/strategy/uid-000000/sid-000000/stop")
        print(response)
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200

        response = self.client.delete("/api/v1.0/strategies/uid-000000/sid-000000")
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200