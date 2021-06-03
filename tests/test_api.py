import unittest
from app import create_app
from base64 import b64encode


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_get_all_users(self):
        credentials = b64encode(b"admin:85114481").decode('utf-8')
        response = self.client.get("/api/v1.0/users",
                                   headers={
                                       "Authorization": f"Basic {credentials}", "API_TOKEN": "85114481"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        from app.models import Users
        assert len(resp_body['users']) == len(Users.users)

    def test_non_admin(self):
        credentials = b64encode(b"juice:85114481").decode('utf-8')
        response = self.client.get("/api/v1.0/users",
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 401

    def test_create_delete_strategies(self):
        new_strategy_list = []

        # create strategy until reach MAX_STRATEGY_NUM
        credentials = b64encode(b"admin:85114481").decode('utf-8')
        for i in range(self.app.config['MAX_STRATEGY_NUM']):
            response = self.client.post("/api/v1.0/strategies",
                                        headers={
                                            "Authorization": f"Basic {credentials}"},
                                        content_type='application/json',
                                        data='{"name": "my_strategy_' + str(i) + '"}')
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 201
            resp_body = response.json
            created_sid = resp_body['strategy']['sid']
            new_strategy_list.append(created_sid)

        response = self.client.get("/api/v1.0/strategies",
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        assert len(resp_body['strategies']
                   ) == self.app.config['MAX_STRATEGY_NUM']

        response = self.client.post("/api/v1.0/strategies",
                                    headers={
                                        "Authorization": f"Basic {credentials}"},
                                    content_type='application/json',
                                    data='{"name": "my_strategy_xx"}')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 429

        response = self.client.get("/api/v1.0/strategies",
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        assert len(resp_body['strategies']
                   ) == self.app.config['MAX_STRATEGY_NUM']

        for sid in new_strategy_list:
            response = self.client.delete("/api/v1.0/strategies/" + str(sid),
                                          headers={
                                              "Authorization": f"Basic {credentials}"},
                                          content_type='application/json')
            assert response.headers["Content-Type"] == "application/json"
            assert response.status_code == 200

    def test_get_strategies_of_a_user(self):
        credentials = b64encode(b"admin:85114481").decode('utf-8')
        response = self.client.get("/api/v1.0/strategies",
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        assert len(resp_body['strategies']) == 0

    def test_get_strategy_by_sid(self):
        credentials = b64encode(b"admin:85114481").decode('utf-8')
        response = self.client.post("/api/v1.0/strategies",
                                    headers={
                                        "Authorization": f"Basic {credentials}"},
                                    content_type='application/json',
                                    data='{"name": "my_strategy_xx"}')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 201
        resp_body = response.json
        created_sid = resp_body['strategy']['sid']

        response = self.client.get("/api/v1.0/strategy/" + created_sid,
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200

        another_user = b64encode(b"juice:85114481").decode('utf-8')
        response = self.client.get("/api/v1.0/strategy/" + created_sid,
                                   headers={
                                       "Authorization": f"Basic {another_user}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 404

        response = self.client.delete("/api/v1.0/strategies/" + str(created_sid),
                                      headers={
                                          "Authorization": f"Basic {credentials}"},
                                      content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200

    def test_get_strategy_field_by_sid_and_key(self):
        credentials = b64encode(b"admin:85114481").decode('utf-8')
        response = self.client.post("/api/v1.0/strategies",
                                    headers={
                                        "Authorization": f"Basic {credentials}"},
                                    content_type='application/json',
                                    data='{"name": "my_strategy_abc"}')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 201
        resp_body = response.json
        created_sid = resp_body['strategy']['sid']

        response = self.client.get("/api/v1.0/strategy/" + created_sid + "/name",
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        assert resp_body['name'] == "my_strategy_abc"

        response = self.client.get("/api/v1.0/strategy/" + created_sid + "/foobar",
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 404

        another_user = b64encode(b"juice:85114481").decode('utf-8')
        response = self.client.get("/api/v1.0/strategy/" + created_sid + "/url",
                                   headers={
                                       "Authorization": f"Basic {another_user}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 404

        response = self.client.get("/api/v1.0/strategy/000000000/url",
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 404

        response = self.client.delete("/api/v1.0/strategies/" + str(created_sid),
                                      headers={
                                          "Authorization": f"Basic {credentials}"},
                                      content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200

    def test_update_strategy_by_sid(self):
        credentials = b64encode(b"admin:85114481").decode('utf-8')
        response = self.client.post("/api/v1.0/strategies",
                                    headers={
                                        "Authorization": f"Basic {credentials}"},
                                    content_type='application/json',
                                    data='{"name": "my_strategy_abc"}')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 201
        resp_body = response.json
        created_sid = resp_body['strategy']['sid']

        response = self.client.get("/api/v1.0/strategy/" + created_sid + "/name",
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        assert resp_body['name'] == "my_strategy_abc"

        response = self.client.put("/api/v1.0/strategy/" + created_sid,
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json',
                                   data='{"name": "//////"}')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200

        response = self.client.get("/api/v1.0/strategy/" + created_sid + "/name",
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        assert resp_body['name'] == "//////"

        response = self.client.delete("/api/v1.0/strategies/" + str(created_sid),
                                      headers={
                                          "Authorization": f"Basic {credentials}"},
                                      content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200

    def test_start_and_stop_theia(self):
        credentials = b64encode(b"admin:85114481").decode('utf-8')
        response = self.client.post("/api/v1.0/strategies",
                                    headers={
                                        "Authorization": f"Basic {credentials}"},
                                    content_type='application/json',
                                    data='{"name": "my_strategy_abc"}')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 201
        resp_body = response.json
        created_sid = resp_body['strategy']['sid']

        response = self.client.put("/api/v1.0/strategy/" + created_sid + "/start",
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        theia_port = resp_body['port']

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

        response = self.client.put("/api/v1.0/strategy/" + created_sid + "/stop",
                                   headers={
                                       "Authorization": f"Basic {credentials}"},
                                   content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200

        response = self.client.delete("/api/v1.0/strategies/" + str(created_sid),
                                      headers={
                                          "Authorization": f"Basic {credentials}"},
                                      content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
