import pytest

import api
from api import ValidationError


class TestCharField:
    field = api.CharField(required=True, nullable=False)

    def test_ok(self):
        assert self.field.validate('text') is None

    def test_incorrect_type(self):
        with pytest.raises(ValidationError):
            self.field.validate(1)


class TestArgumentsField:
    field = api.ArgumentsField(required=True, nullable=False)

    def test_ok(self):
        assert self.field.validate({}) is None

    def test_incorrect_type(self):
        with pytest.raises(ValidationError):
            self.field.validate('invalid_type')


class TestEmailField:
    field = api.EmailField(required=True, nullable=False)

    def test_ok(self):
        assert self.field.validate('test@mail.com') is None

    def test_incorrect_form(self):
        with pytest.raises(ValidationError):
            self.field.validate('testmail.com')


class TestPhoneField:
    field = api.PhoneField(required=True, nullable=False)

    def test_ok(self):
        assert self.field.validate('79210010033') is None

    def test_incorrect_start_num(self):
        with pytest.raises(ValidationError):
            self.field.validate('89232344123')

    def test_incorrect_length(self):
        with pytest.raises(ValidationError):
            self.field.validate('7923223')

    def test_incorrect_type(self):
        with pytest.raises(ValidationError):
            self.field.validate(2.5)


class TestDateField:
    field = api.DateField(required=True, nullable=False)

    def test_ok(self):
        assert self.field.validate('21.01.1970') is None

    def test_incorrect_value(self):
        with pytest.raises(ValidationError):
            self.field.validate('21011970')


class TestBirthDayField:
    field = api.BirthDayField(required=True, nullable=False)

    def test_ok(self):
        assert self.field.validate('21.01.1970') is None

    def test_incorrect_value(self):
        with pytest.raises(ValidationError):
            self.field.validate('21011970')

    def test_incorrect_age(self):
        with pytest.raises(ValidationError):
            self.field.validate('21.01.1800')


class TestGenderField:
    field = api.GenderField(required=True, nullable=False)

    def test_ok(self):
        assert self.field.validate(0) is None

    def test_incorrect_type(self):
        with pytest.raises(ValidationError):
            self.field.validate('1')

    def test_incorrect_value(self):
        with pytest.raises(ValidationError):
            self.field.validate(3)


class TestClientIDsField:
    field = api.ClientIDsField(required=True, nullable=False)

    def test_ok(self):
        assert self.field.validate([1, 2, 3, 4]) is None

    def test_incorrect_type(self):
        with pytest.raises(ValidationError):
            self.field.validate('1')

    def test_empty_list(self):
        with pytest.raises(ValidationError):
            self.field.validate([])

    def test_incorrect_value(self):
        with pytest.raises(ValidationError):
            self.field.validate([1, '2', 3, 'a'])


if __name__ == "__main__":
    pytest.main()
