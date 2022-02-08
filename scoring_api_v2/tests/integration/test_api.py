import pytest
import hashlib
import datetime

import api
from store import Store


context = {}
headers = {}
store = Store()

test_bad_auth_data = [
    ({"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}}),
    ({"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}}),
    ({"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}})
]

test_invalid_method_request_data = [
    ({"account": "horns&hoofs", "login": "h&f", "method": "online_score"}),
    ({"account": "horns&hoofs", "login": "h&f", "arguments": {}}),
    ({"account": "horns&hoofs", "method": "online_score", "arguments": {}})
]

test_invalid_score_request_data = [
    ({}),
    ({"phone": "79175002040"}),
    ({"phone": "89175002040", "email": "stupnikov@otus.ru"}),
    ({"phone": "79175002040", "email": "stupnikovotus.ru"}),
    ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1}),
    ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"}),
    ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"}),
    ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"}),
    ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": 1}),
    ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
      "first_name": "s", "last_name": 2}),
    ({"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"}),
    ({"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2})
]

test_ok_score_arguments_data = [
    ({"phone": "79175002040", "email": "stupnikov@otus.ru"}),
    ({"phone": 79175002040, "email": "stupnikov@otus.ru"}),
    ({"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"}),
    ({"gender": 0, "birthday": "01.01.2000"}),
    ({"gender": 2, "birthday": "01.01.2000"}),
    ({"first_name": "a", "last_name": "b"}),
    ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
      "first_name": "a", "last_name": "b"})
]

test_ok_score_admin_arguments_data = [
    ({"phone": "79175002040", "email": "stupnikov@otus.ru"}),
]

test_invalid_interests_arguments_data = [
    ({}),
    ({"date": "20.07.2017"}),
    ({"client_ids": [], "date": "20.07.2017"}),
    ({"client_ids": {1: 2}, "date": "20.07.2017"}),
    ({"client_ids": ["1", "2"], "date": "20.07.2017"}),
    ({"client_ids": [1, 2], "date": "XXX"}),
]

test_ok_interests_arguments_data = [
    ({"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")}),
    #({"client_ids": [1, 2], "date": "19.07.2017"}),
    #({"client_ids": [0]}),
]


def set_valid_auth(request):
    if request.get("login") == api.ADMIN_LOGIN:
        request["token"] = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H").encode('utf-8')
                                          + api.ADMIN_SALT.encode('utf-8')).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(msg.encode('utf-8')).hexdigest()


def test_empty_request():
    request = {}
    _, code = api.method_handler({"body": request, "headers": headers}, context, store)
    assert api.INVALID_REQUEST == code


@pytest.mark.parametrize("request_data", test_bad_auth_data)
def test_bad_auth(request_data):
    _, code = api.method_handler({"body": request_data, "headers": headers}, context, store)
    assert api.FORBIDDEN == code


@pytest.mark.parametrize("request_data", test_invalid_method_request_data)
def test_invalid_method_request(request_data):
    set_valid_auth(request_data)
    response, code = api.method_handler({"body": request_data, "headers": headers}, context, store)
    assert api.INVALID_REQUEST == code
    assert len(response)


@pytest.mark.parametrize("arguments_data", test_invalid_score_request_data)
def test_invalid_score_request(arguments_data):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments_data}
    set_valid_auth(request)
    response, code = api.method_handler({"body": request, "headers": headers}, context, store)
    assert api.INVALID_REQUEST == code
    assert len(response)


@pytest.mark.parametrize("arguments_data", test_ok_score_arguments_data)
def test_ok_score_request(arguments_data):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments_data}
    set_valid_auth(request)
    response, code = api.method_handler({"body": request, "headers": headers}, context, store)
    score = response.get("score")
    assert api.OK == code
    assert isinstance(score, (int, float)) and score >= 0
    assert sorted(context["has"]) == sorted(arguments_data.keys())


@pytest.mark.parametrize("arguments_data", test_ok_score_admin_arguments_data)
def test_ok_score_admin_request(arguments_data):
    request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments_data}
    set_valid_auth(request)
    response, code = api.method_handler({"body": request, "headers": headers}, context, store)
    score = response.get("score")
    assert api.OK == code
    assert score == 42
    assert sorted(context["has"]) == sorted(arguments_data.keys())


@pytest.mark.parametrize("arguments_data", test_invalid_interests_arguments_data)
def test_invalid_interests_request(arguments_data):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments_data}
    set_valid_auth(request)
    response, code = api.method_handler({"body": request, "headers": headers}, context, store)
    assert api.INVALID_REQUEST == code
    assert len(response)


# TODO: Доработать тест
@pytest.mark.parametrize("arguments_data", test_ok_interests_arguments_data)
def test_ok_interests_request(arguments_data):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments_data}
    set_valid_auth(request)
    response, code = api.method_handler({"body": request, "headers": headers}, context, store)
    assert api.OK == code
    #assert len(response)


if __name__ == "__main__":
    pytest.main()
