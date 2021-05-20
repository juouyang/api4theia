import unittest
from app import create_app
from base64 import b64encode


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()


    def test_get_all_users(self):
        credentials = b64encode(b"admin:85114481").decode('utf-8')
        response = self.client.get("/api/v1.0/users",
                        headers={"Authorization": f"Basic {credentials}"},
                        content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        assert len(resp_body['users']) == 12

    def test_non_admin(self):
        credentials = b64encode(b"juice:85114481").decode('utf-8')
        response = self.client.get("/api/v1.0/users",
                        headers={"Authorization": f"Basic {credentials}"},
                        content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 401


    def test_get_strategies_of_a_user(self):
        credentials = b64encode(b"admin:85114481").decode('utf-8')
        response = self.client.get("/api/v1.0/strategies",
                        headers={"Authorization": f"Basic {credentials}"},
                        content_type='application/json')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        resp_body = response.json
        assert len(resp_body['strategies']) == 0


    def test_get_strategy_by_sid(self):
        credentials = b64encode(b"admin:85114481").decode('utf-8')
        response = self.client.post("/api/v1.0/strategies",
                        headers={"Authorization": f"Basic {credentials}"},
                        content_type='application/json',
                        data='{"name": "my_strategy_xx"}')
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 201
        resp_body = response.json
        created_sid = resp_body['strategy']['sid']