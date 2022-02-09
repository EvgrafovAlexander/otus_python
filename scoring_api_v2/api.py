#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import datetime
import logging
import hashlib
import uuid
from abc import ABC, abstractmethod
from dateutil.relativedelta import relativedelta
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler

import scoring
from store import Store

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
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


# --- Exceptions ---
class ValidationError(Exception):
    pass


# --- Fields ---
class AbstractField(ABC):
    def __init__(self, required, nullable):
        self.required = required
        self.nullable = nullable

    @abstractmethod
    def validate(self, value):
        pass


class CharField(AbstractField):
    def validate(self, value):
        if not isinstance(value, str):
            raise ValidationError("Value must be str type")


class ArgumentsField(AbstractField):
    def validate(self, value):
        if not isinstance(value, dict):
            raise ValidationError("Value must be dict type")


class EmailField(CharField):
    def validate(self, value):
        super().validate(value)
        if '@' not in value:
            raise ValidationError('Value must exist @.')


class PhoneField(AbstractField):
    def validate(self, value):
        if not isinstance(value, str | int):
            raise ValidationError("Value must be str or int type")
        value = str(value)
        if len(value) != 11:
            raise ValidationError("Length must be equal 11 symbols")
        if value[0] != '7':
            raise ValidationError("Thirst symbol must be 7")


class DateField(AbstractField):
    def validate(self, value):
        try:
            isinstance(datetime.datetime.strptime(value, "%d.%m.%Y"), datetime.date)
        except:
            raise ValidationError("Value must be datetime format: DD.MM.YYYY")


class BirthDayField(AbstractField):
    def validate(self, value):
        try:
            value = datetime.datetime.strptime(value, "%d.%m.%Y")
            if not relativedelta(datetime.datetime.now(), value).years < 70:
                raise ValidationError('Age must be < 70.')
        except:
            raise ValidationError("Value must be datetime format: DD.MM.YYYY")


class GenderField(AbstractField):
    def validate(self, value):
        if not isinstance(value, int):
            raise ValidationError("Value must be int type")
        if value not in (0, 1, 2):
            raise ValidationError("Value must be in 0, 1, 2")


class ClientIDsField(AbstractField):
    def validate(self, value):
        if not isinstance(value, list):
            raise ValidationError("Value must be list type")
        if not value:
            raise ValidationError("Value must not be empty")
        if not all(isinstance(x, int) for x in value):
            raise ValidationError("Values in the list must be integers")


# --- Requests ---
class Meta(type):
    def __new__(mcs, name, bases, attrs):
        field_list = []
        for k, v in attrs.items():
            if isinstance(v, AbstractField):
                v.name = k
                field_list.append(v)

        cls = super(Meta, mcs).__new__(mcs, name, bases, attrs)
        cls.fields = field_list
        return cls


class Base(metaclass=Meta):
    def __init__(self, args):
        self.args = args
        self.errors = {}

    def validate(self):
        for field in self.fields:
            name = field.name
            value = self.args.get(name)
            setattr(self, name, value)

            if value is None:
                if field.required:
                    self.errors[name] = "Required value not found"
                elif not field.nullable:
                    self.errors[name] = "Required value can't be zero"
            else:
                try:
                    field.validate(value)
                except Exception as e:
                    self.errors[name] = str(e)

    def is_valid(self):
        self.validate()
        return not self.errors

    def get_found_errors(self):
        return str(self.errors)


class MethodRequest(Base):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class ClientsInterestsRequest(Base):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Base):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self):
        super().validate()
        if (self.phone and self.email) \
                or (self.first_name and self.last_name) \
                or (self.gender is not None and self.birthday):
            return
        self.errors['Combinations Error'] = 'Required field combinations not found: phone and email,' \
                                            ' first name and last name, gender and birthday'


# --- Request Handlers ---
class RequestHandler(ABC):
    @abstractmethod
    def get_response(self, data, request, context, store):
        pass

    @staticmethod
    @abstractmethod
    def get_context(data):
        pass


class OnlineScoreRequestHandler(RequestHandler):
    def get_response(self, data, request, context, store):
        if not data.is_valid():
            return data.get_found_errors(), INVALID_REQUEST

        if request.is_admin:
            score = 42
        else:
            score = scoring.get_score(store, data.phone, data.email, data.birthday,
                                      data.gender, data.first_name, data.last_name)

        context['has'] = self.get_context(data)
        return {'score': score}, OK

    @staticmethod
    def get_context(data):
        context = []
        for attr in data.fields:
            attribute = getattr(data, attr.name)
            if attribute is not None:
                context.append(attr.name)
        return context


class ClientsInterestsRequestHandler(RequestHandler):
    def get_response(self, data, request, context, store):
        if not data.is_valid():
            return data.get_found_errors(), INVALID_REQUEST

        result = dict()
        for client_id in data.client_ids:
            interests = scoring.get_interests(store, client_id)
            result[client_id] = interests
        context['nclients'] = self.get_context(data)
        return result, OK

    @staticmethod
    def get_context(data):
        context = len(data.client_ids) if data.client_ids else 0
        return context


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode('utf-8')).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    requests = {
        'online_score': {
            'method': OnlineScoreRequest,
            'handler': OnlineScoreRequestHandler
        },
        'clients_interests': {
            'method': ClientsInterestsRequest,
            'handler': ClientsInterestsRequestHandler
        },
    }

    if not (request['body'] or request['headers']):
        return None, INVALID_REQUEST

    request = MethodRequest(request['body'])
    if not request.is_valid():
        return request.get_found_errors(), INVALID_REQUEST
    if not check_auth(request):
        return ERRORS[FORBIDDEN], FORBIDDEN

    data = requests[request.method]['method'](request.arguments)
    handler = requests[request.method]['handler']

    return handler().get_response(data, request, ctx, store)


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = Store()

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
                    response, code = self.router[path]({"body": request, "headers": self.headers},
                                                       context,
                                                       self.store)
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
