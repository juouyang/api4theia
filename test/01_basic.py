import pytest
import requests
import json

def test_get_all_strategies():
    response = requests.get("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategies/all")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['strategies']) == 3

    response = requests.get("http://user1:85114481@127.0.0.1:5000/api/v1.0/strategies/all")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 401

def test_get_strategies_of_user():
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

def test_get_strategy_field_by_key():
    response = requests.get("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/name")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['name'] == "my_strategy_a"

    response = requests.get("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/url")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['url'] == "http://192.168.233.136:30000"

    response = requests.get("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/foobar")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404

    response = requests.get("http://user1:85114481@127.0.0.1:5000/api/v1.0/strategy/YJMDUH9zuwXf8c6KT2CDEV/url")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404

    response = requests.get("http://admin:85114481@127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW/url")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 404

    response = requests.get("http://user1:85114481@127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW/name")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['name'] == "my_strategy_a"

    response = requests.get("http://user1:85114481@127.0.0.1:5000/api/v1.0/strategy/9JYN5ycAEfoVNTkFxFQQxW/url")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['url'] == "http://192.168.233.136:30002"

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

def test_get_all_users():
    response = requests.get("http://admin:85114481@127.0.0.1:5000/api/v1.0/users")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['users']) == 2

    response = requests.get("http://user1:85114481@127.0.0.1:5000/api/v1.0/users")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 401