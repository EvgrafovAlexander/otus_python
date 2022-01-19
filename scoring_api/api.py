#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import datetime
import logging
import hashlib
import uuid
from abc import ABC
from collections import namedtuple
from dateutil.relativedelta import relativedelta
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler

import scoring

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
INVALID_VALUE = -1
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

ValidatedValue = namedtuple('ValidatedValue', 'value is_valid')


class AbstractField(ABC):
    def __init__(self, value, required, nullable):
        self.value = value
        self.required = required
        self.nullable = nullable

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if value is None:
            if self.required or not self.nullable:
                self.value = ValidatedValue(value, False)
            else:
                self.value = ValidatedValue(value, True)
        elif self.is_valid(value):
            self.value = ValidatedValue(value, True)
        else:
            self.value = ValidatedValue(value, False)

    @staticmethod
    def is_valid(value):
        pass


class CharField(AbstractField):
    @staticmethod
    def is_valid(value):
        return isinstance(value, str)


class ArgumentsField(object):
    def __init__(self, required, nullable):
        self.required = required
        self.required = nullable


class EmailField(CharField):
    @staticmethod
    def is_valid(value):
        return isinstance(value, str) and '@' in value


class PhoneField(AbstractField):
    @staticmethod
    def is_valid(value):
        if isinstance(value, str | int):
            value = str(value)
            return len(value) == 11 and value[0] == '7'
        return False


class DateField(AbstractField):
    @staticmethod
    def is_valid(value):
        try:
            return isinstance(datetime.datetime.strptime(value, "%d.%m.%Y"), datetime.date)
        except:
            return False


class BirthDayField(AbstractField):
    @staticmethod
    def is_valid(value):
        try:
            value = datetime.datetime.strptime(value, "%d.%m.%Y")
            return relativedelta(datetime.datetime.now(), value).years < 70
        except:
            return False


class GenderField(AbstractField):
    @staticmethod
    def is_valid(value):
        return isinstance(value, int) and value in (0, 1, 2)


class ClientIDsField(object):
    def __init__(self, value, required):
        self.value = value
        self.required = required

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if value is None and self.required:
            self.value = ValidatedValue(value, False)
        elif self.is_valid(value):
            self.value = ValidatedValue(value, True)
        else:
            self.value = ValidatedValue(value, False)

    @staticmethod
    def is_valid(value):
        if isinstance(value, list) and value and all(isinstance(x, int) for x in value):
            return True
        return False


class ClientsInterestsRequest(object):
    client_ids = ClientIDsField(value=None, required=True)
    date = DateField(value=None, required=False, nullable=True)

    def __init__(self, client_ids, date):
        self.client_ids = client_ids
        self.date = date

    @property
    def is_valid(self):
        if self.client_ids.is_valid and self.date.is_valid:
            return True
        return False


class OnlineScoreRequest(object):
    first_name = CharField(value=None, required=False, nullable=True)
    last_name = CharField(value=None, required=False, nullable=True)
    email = EmailField(value=None, required=False, nullable=True)
    phone = PhoneField(value=None, required=False, nullable=True)
    birthday = BirthDayField(value=None, required=False, nullable=True)
    gender = GenderField(value=None, required=False, nullable=True)

    def __init__(self, first_name, last_name, email, phone, birthday, gender):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.birthday = birthday
        self.gender = gender

    @property
    def is_valid(self):
        if self.phone.is_valid and self.email.is_valid and self.first_name.is_valid and self.last_name.is_valid \
                and self.gender.is_valid and self.birthday.is_valid:

            if (self.phone.value and self.email.value) \
                    or (self.first_name.value and self.last_name.value) \
                    or (self.gender.value is not None and self.birthday.value):
                return True
        return False

    def get_context(self):
        context = []
        for attr in dir(self):
            if not (attr.startswith('_')
                    or attr.startswith('is_valid') or attr.startswith('get_context')):
                attribute = getattr(self, attr)
                if attribute.value is not None and attribute.is_valid:
                    context.append(attr)
        return {'has': context}


class MethodRequest(object):
    account = CharField(value=None, required=False, nullable=True)
    login = CharField(value=None, required=True, nullable=True)
    token = CharField(value=None, required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(value=None, required=True, nullable=False)

    def __init__(self, account, login, token, arguments, method):
        self.account = account
        self.login = login
        self.token = token
        self.arguments = arguments
        self.method = method

    @property
    def is_admin(self):
        return self.login.value == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512((request.account.value + request.login.value + SALT).encode('utf-8')).hexdigest()
    if digest == request.token.value:
        return True
    return False


def method_handler(request, ctx, store):
    response, code = None, None
    if not (request['body'] or request['headers']):
        return ERRORS[INVALID_REQUEST], INVALID_REQUEST

    if not request['body'].keys() >= {'login', 'method', 'token', 'arguments'}:
        return ERRORS[INVALID_REQUEST], INVALID_REQUEST

    headers = request['headers']
    body = request['body']
    request = MethodRequest(body.get('account', None), body['login'], body['token'], body['arguments'], body['method'])

    if not check_auth(request):
        return ERRORS[FORBIDDEN], FORBIDDEN

    args = request.arguments

    if request.method.value == 'online_score':
        score_request = OnlineScoreRequest(args.get('first_name', None),
                                           args.get('last_name', None),
                                           args.get('email', None),
                                           args.get('phone', None),
                                           args.get('birthday', None),
                                           args.get('gender', None))

        if request.is_admin:
            score = 42
        else:
            score = scoring.get_score(store, score_request.phone, score_request.email, score_request.birthday,
                                      score_request.gender, score_request.first_name, score_request.last_name)

    elif request.method.value == 'clients_interests':
        score_request = ClientsInterestsRequest(args.get('client_ids', None),
                                                args.get('date', None))
    else:
        return ERRORS[INVALID_REQUEST], INVALID_REQUEST

    if not score_request.is_valid:
        return ERRORS[INVALID_REQUEST], INVALID_REQUEST

    code = OK
    response = {'score': score, 'context': score_request.get_context()}

    # exec('а = score_request.phone')
    # asf = ', '.join(i for i in dir(score_request) if not i.startswith('__'))

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
