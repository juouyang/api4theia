import pytest
import requests
import json


def test_get_strategies_of_a_user():
    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 2

    response = requests.get(
        "https://user1:85114481@127.0.0.1:5000/api/v1.0/strategies", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 1


def test_get_strategy_by_sid():
    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200

    response = requests.get(
        "https://user1:85114481@127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404

    response = requests.get(
        "https://user1:85114481@127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404


def test_get_strategy_field_by_sid_and_key():
    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/name", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['name'] == "my_strategy_a"

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/url", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['url'] == "http://192.168.233.136:30000"

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/foobar", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404

    response = requests.get(
        "https://user1:85114481@127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/url", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW/url", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404

    response = requests.get(
        "https://user1:85114481@127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW/name", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['name'] == "my_strategy_a"

    response = requests.get(
        "https://user1:85114481@127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW/url", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['url'] == "http://192.168.233.136:30002"


def test_create_delete_a_strategy():
    response = requests.post("https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies",
                             data='{"name": "my_strategy_c"}',
                             headers={'Content-Type': 'application/json'}, verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 201
    resp_body = response.json()
    created_sid = resp_body['strategy']['sid']

    response = requests.post("https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies",
                             data='{"name": "my_strategy_c"}',
                             headers={'Content-Type': 'application/json'}, verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 429

    response = requests.get(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 3

    response = requests.delete(
        "https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies/" + str(created_sid), verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200

    response = requests.post("https://admin:85114481@127.0.0.1:5000/api/v1.0/strategies",
                             data='{"name": "my_strategy_c"}',
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
    assert len(resp_body['users']) == 2

    response = requests.get(
        "https://user1:85114481@127.0.0.1:5000/api/v1.0/users", verify=False)
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 401
