import datetime
import hashlib

import api
import pytest
from store import Store

context = {}
headers = {}
store = Store()


def set_valid_auth(request):
    if request.get("login") == api.ADMIN_LOGIN:
        request["token"] = hashlib.sha512(
            datetime.datetime.now().strftime("%Y%m%d%H").encode("utf-8") + api.ADMIN_SALT.encode("utf-8")
        ).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(msg.encode("utf-8")).hexdigest()


def idfn(arg):
    return str(arg)


def test_empty_request():
    request = {}
    _, code = api.method_handler({"body": request, "headers": headers}, context, store)
    assert api.INVALID_REQUEST == code


@pytest.mark.parametrize(
    "request_data",
    [
        ({"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}}),
        ({"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}}),
        ({"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}}),
    ],
    ids=idfn,
)
def test_bad_auth(request_data):
    _, code = api.method_handler({"body": request_data, "headers": headers}, context, store)
    assert api.FORBIDDEN == code


@pytest.mark.parametrize(
    "request_data",
    [
        ({"account": "horns&hoofs", "login": "h&f", "method": "online_score"}),
        ({"account": "horns&hoofs", "login": "h&f", "arguments": {}}),
        ({"account": "horns&hoofs", "method": "online_score", "arguments": {}}),
    ],
    ids=idfn,
)
def test_invalid_method_request(request_data):
    set_valid_auth(request_data)
    response, code = api.method_handler({"body": request_data, "headers": headers}, context, store)
    assert api.INVALID_REQUEST == code
    assert len(response)


@pytest.mark.parametrize(
    "arguments",
    [
        ({}),
        ({"phone": "79175002040"}),
        ({"phone": "89175002040", "email": "stupnikov@otus.ru"}),
        ({"phone": "79175002040", "email": "stupnikovotus.ru"}),
        ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1}),
        ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"}),
        ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"}),
        ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"}),
        (
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "01.01.2000",
                "first_name": 1,
            }
        ),
        (
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "01.01.2000",
                "first_name": "s",
                "last_name": 2,
            }
        ),
        ({"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"}),
        ({"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2}),
    ],
    ids=idfn,
)
def test_invalid_score_request(arguments):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = api.method_handler({"body": request, "headers": headers}, context, store)
    assert api.INVALID_REQUEST == code
    assert len(response)


@pytest.mark.parametrize(
    "arguments",
    [
        ({"phone": "79175002040", "email": "stupnikov@otus.ru"}),
        ({"phone": 79175002040, "email": "stupnikov@otus.ru"}),
        ({"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"}),
        ({"gender": 0, "birthday": "01.01.2000"}),
        ({"gender": 2, "birthday": "01.01.2000"}),
        ({"first_name": "a", "last_name": "b"}),
        (
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "01.01.2000",
                "first_name": "a",
                "last_name": "b",
            }
        ),
    ],
    ids=idfn,
)
def test_ok_score_request(arguments):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = api.method_handler({"body": request, "headers": headers}, context, store)
    score = response.get("score")
    assert api.OK == code
    assert isinstance(score, (int, float)) and score >= 0
    assert sorted(context["has"]) == sorted(arguments.keys())


@pytest.mark.parametrize(
    "arguments",
    [
        ({"phone": "79175002040", "email": "stupnikov@otus.ru"}),
    ],
    ids=idfn,
)
def test_ok_score_admin_request(arguments):
    request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = api.method_handler({"body": request, "headers": headers}, context, store)
    score = response.get("score")
    assert api.OK == code
    assert score == 42
    assert sorted(context["has"]) == sorted(arguments.keys())


@pytest.mark.parametrize(
    "arguments",
    [
        ({}),
        ({"date": "20.07.2017"}),
        ({"client_ids": [], "date": "20.07.2017"}),
        ({"client_ids": {1: 2}, "date": "20.07.2017"}),
        ({"client_ids": ["1", "2"], "date": "20.07.2017"}),
        ({"client_ids": [1, 2], "date": "XXX"}),
    ],
    ids=idfn,
)
def test_invalid_interests_request(arguments):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = api.method_handler({"body": request, "headers": headers}, context, store)
    assert api.INVALID_REQUEST == code
    assert len(response)


@pytest.mark.parametrize(
    "arguments",
    [
        ({"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")}),
        ({"client_ids": [1, 2], "date": "19.07.2017"}),
        ({"client_ids": [0]}),
    ],
    ids=idfn,
)
def test_ok_interests_request(arguments):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = api.method_handler({"body": request, "headers": headers}, context, store)
    assert api.OK == code
    assert len(response)


if __name__ == "__main__":
    pytest.main()
