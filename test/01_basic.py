import pytest
import requests
import json

@pytest.mark.order(1)
def test_get_all_strategies_by_admin_equals_200():
    response = requests.get("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategies/all")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 3

    response = requests.get("http://user1:85114481@127.0.0.1:5000/api/v1.0/strategies/all")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 401

@pytest.mark.order(2)
def test_get_strategies_by_user_equals_200():
    response = requests.get("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategies")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 2

    response = requests.get("http://user1:85114481@127.0.0.1:5000/api/v1.0/strategies")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 1

@pytest.mark.order(3)
def test_create_delete_a_strategy():
    response = requests.post("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategies",
                                data='{"name": "my_strategy_c"}',
                                headers={'Content-Type': 'application/json'})
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 201
    resp_body = response.json()
    created_sid = resp_body['strategy']['sid']

    response = requests.post("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategies",
                                data='{"name": "my_strategy_c"}',
                                headers={'Content-Type': 'application/json'})
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 429

    response = requests.get("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategies/all")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 4

    response = requests.get("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategies")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 3

    response = requests.delete("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategies/" + str(created_sid))
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200

    response = requests.post("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategies",
                                data='{"name": "my_strategy_c"}',
                                headers={'Content-Type': 'application/json'})
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 201
    resp_body = response.json()
    created_sid = resp_body['strategy']['sid']

    response = requests.delete("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategies/" + str(created_sid))
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
