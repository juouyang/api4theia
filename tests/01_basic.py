import pytest
import requests
import json

service_addr = "pve.dev.net"

def test_get_strategies_of_a_user():
    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 0

    response = requests.get(
        "https://juice:85114481@127.0.0.1:5000/api/v1.0/strategies", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 0

def test_get_strategy_by_sid():
    response = requests.post("https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies",
                             data='{"name": "my_strategy_xx"}',
                             headers={'Content-Type': 'application/json'}, verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 201
    resp_body = response.json()
    created_sid = resp_body['strategy']['sid']

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/" + created_sid, verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200

    response = requests.get(
        "https://juice:85114481@127.0.0.1:5000/api/v1.0/strategy/" + created_sid, verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404

    response = requests.delete(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies/" + str(created_sid), verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200


def test_get_strategy_field_by_sid_and_key():
    response = requests.post("https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies",
                             data='{"name": "my_strategy_a"}',
                             headers={'Content-Type': 'application/json'}, verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 201
    resp_body = response.json()
    created_sid = resp_body['strategy']['sid']

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/" + created_sid + "/name", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['name'] == "my_strategy_a"

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/" + created_sid + "/url", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['url'] == "https://" + service_addr + ":30000"

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/" + created_sid + "/foobar", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404

    response = requests.get(
        "https://juice:85114481@127.0.0.1:5000/api/v1.0/strategy/" + created_sid + "/url", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/0000000000000000/url", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404

    response = requests.delete(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies/" + str(created_sid), verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200


def test_create_delete_a_strategy():
    new_strategy_list = []

    # create strategy until reach 100
    for i in range(100):
        response = requests.post("https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies",
                             data='{"name": "my_strategy_' + str(i) + '"}',
                             headers={'Content-Type': 'application/json'}, verify=False)
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 201
        resp_body = response.json()
        created_sid = resp_body['strategy']['sid']
        new_strategy_list.append(created_sid)

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 100

    response = requests.post("https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies",
                             data='{"name": "my_strategy_xx"}',
                             headers={'Content-Type': 'application/json'}, verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 429

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 100

    for sid in new_strategy_list:
        response = requests.delete(
            "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies/" + sid, verify=False)
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200

    response = requests.post("https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies",
                             data='{"name": "my_strategy_xx"}',
                             headers={'Content-Type': 'application/json'}, verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 201
    resp_body = response.json()
    created_sid = resp_body['strategy']['sid']

    response = requests.delete(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies/" + str(created_sid), verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200


def test_get_all_users():
    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/users", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['users']) == 12

    response = requests.get(
        "https://juice:85114481@127.0.0.1:5000/api/v1.0/users", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 401
