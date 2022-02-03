#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import datetime
import logging
import hashlib
import uuid
from abc import ABC
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


class ValidationError(Exception):
    pass


class AbstractField(ABC):
    def __init__(self, required, nullable):
        self.value = None
        self.required = required
        self.nullable = nullable

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if value is None:
            if self.required:
                raise ValidationError("Required value not found")
            elif not self.nullable:
                raise ValidationError("Required value can't be zero")
            else:
                self.value = value
        else:
            self.is_valid(value)
            self.value = value

    def is_valid(self, value):
        pass


class CharField(AbstractField):
    def is_valid(self, value):
        if not isinstance(value, str):
            raise ValidationError("Value must be str type")


class ArgumentsField(AbstractField):
    def is_valid(self, value):
        if not isinstance(value, dict):
            raise ValidationError("Value must be dict type")


class EmailField(CharField):
    def is_valid(self, value):
        super().is_valid(value)
        if '@' not in value:
            raise ValidationError('Value must exist @.')


class PhoneField(AbstractField):
    def is_valid(self, value):
        if not isinstance(value, str | int):
            raise TypeError("Value must be str or int type")
        value = str(value)
        if len(value) != 11:
            raise ValidationError("Length must be equal 11 symbols")
        if value[0] != '7':
            raise ValidationError("Thirst symbol must be 7")


class DateField(AbstractField):
    def is_valid(self, value):
        try:
            isinstance(datetime.datetime.strptime(value, "%d.%m.%Y"), datetime.date)
        except:
            raise ValidationError("Value must be datetime format: DD.MM.YYYY")


class BirthDayField(AbstractField):
    def is_valid(self, value):
        try:
            value = datetime.datetime.strptime(value, "%d.%m.%Y")
            if not relativedelta(datetime.datetime.now(), value).years < 70:
                raise ValidationError('Age must be < 70.')
        except:
            raise ValidationError("Value must be datetime format: DD.MM.YYYY")


class GenderField(AbstractField):
    def is_valid(self, value):
        if not isinstance(value, int):
            raise ValidationError("Value must be int type")
        if value not in (0, 1, 2):
            raise ValidationError("Value must be in 0, 1, 2")


class ClientIDsField(AbstractField):
    def is_valid(self, value):
        if not isinstance(value, list):
            raise ValidationError("Value must be list type")
        if not value:
            raise ValidationError("Value must not be empty")
        if not all(isinstance(x, int) for x in value):
            raise ValidationError("Values in the list must be integers")


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
        for v in self.fields:
            setattr(self, v.name, args.get(v.name, None))


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

    def validate(self):
        for attr in self.fields:
            attribute = getattr(self, attr.name)
            if not attribute.is_valid:
                return False, {'error': f'Incorrected value {attribute.value} if field {attr}'}
        return True, None


    def get_context(self):
        context = len(self.client_ids) if self.client_ids else 0
        return context

    def get_response(self, request, context, store):
        result = dict()
        for client_id in self.client_ids:
            interests = scoring.get_interests(None, None)
            result[client_id] = interests
        context['nclients'] = self.get_context()
        return result, OK


class OnlineScoreRequest(Base):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self):
        if (self.phone and self.email) \
                or (self.first_name and self.last_name) \
                or (self.gender is not None and self.birthday):
            return True, None
        return False, {'error': 'Required field combinations not found: phone and email,'
                                ' first name and last name, gender and birthday'}

    def get_context(self):
        context = []
        for attr in self.fields:
            attribute = getattr(self, attr.name)
            if attribute is not None:
                context.append(attr.name)
        return context

    def get_response(self, request, context, store):
        if request.is_admin:
            score = 42
        else:
            score = scoring.get_score(store, self.phone, self.email, self.birthday,
                                      self.gender, self.first_name, self.last_name)

            is_valid, valid_info = self.validate()
            if not is_valid:
                return valid_info, INVALID_REQUEST

        context['has'] = self.get_context()
        return {'score': score}, OK


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode('utf-8')).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    if not (request['body'] or request['headers']):
        return None, INVALID_REQUEST

    try:
        request = MethodRequest(request['body'])

        if not check_auth(request):
            return ERRORS[FORBIDDEN], FORBIDDEN

        args = request.arguments

        if request.method == 'online_score':
            score_request = OnlineScoreRequest(args)
        elif request.method == 'clients_interests':
            score_request = ClientsInterestsRequest(args)
        else:
            return ERRORS[INVALID_REQUEST], INVALID_REQUEST
    except Exception:
        return ERRORS[INVALID_REQUEST], INVALID_REQUEST

    return score_request.get_response(request, ctx, store)


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
