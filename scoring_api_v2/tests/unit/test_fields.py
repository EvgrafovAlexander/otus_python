import pytest

import api
from api import ValidationError


class TestAbstractField:
    field = api.AbstractField(required=True, nullable=False)

    def test_ok(self):
        self.field = 'text'
        assert self.field == 'text'

    def test_required_with_none(self):
        with pytest.raises(ValidationError):
            self.field = None


class TestCharField:
    field = api.CharField(required=True, nullable=False)

    def test_ok(self):
        self.field = 'text'
        assert self.field == 'text'

    def test_incorrect_type(self):
        with pytest.raises(TypeError):
            self.field = 1


class TestArgumentsField:
    field = api.ArgumentsField(required=True, nullable=False)

    def test_ok(self):
        self.field = {}
        assert self.field == {}

    def test_incorrect_type(self):
        with pytest.raises(TypeError):
            self.field = 'invalid_type'


class TestEmailField:
    field = api.EmailField(required=True, nullable=False)

    def test_ok(self):
        self.field = 'test@mail.com'
        assert self.field == 'test@mail.com'

    def test_incorrect_form(self):
        with pytest.raises(ValidationError):
            self.field = 'testmail.com'


class TestPhoneField:
    field = api.PhoneField(required=True, nullable=False)

    def test_ok(self):
        self.field = '79210010033'
        assert self.field == '79210010033'

    def test_incorrect_start_num(self):
        with pytest.raises(ValidationError):
            self.field = '89232344123'

    def test_incorrect_length(self):
        with pytest.raises(ValidationError):
            self.field = '7923223'

    def test_incorrect_type(self):
        with pytest.raises(TypeError):
            self.field = 2.5


class TestDateField:
    field = api.DateField(required=True, nullable=False)

    def test_ok(self):
        self.field = '21.01.1970'
        assert self.field == '21.01.1970'

    def test_incorrect_value(self):
        with pytest.raises(ValueError):
            self.field = '21011970'


class TestBirthDayField:
    field = api.BirthDayField(required=True, nullable=False)

    def test_ok(self):
        self.field = '21.01.1970'
        assert self.field == '21.01.1970'

    def test_incorrect_value(self):
        with pytest.raises(ValueError):
            self.field = '21011970'

    def test_incorrect_age(self):
        with pytest.raises(ValueError):
            self.field = '21.01.1800'


class TestGenderField:
    field = api.GenderField(required=True, nullable=False)

    def test_ok(self):
        self.field = 0
        assert self.field == 0

    def test_incorrect_type(self):
        with pytest.raises(TypeError):
            self.field = '1'

    def test_incorrect_value(self):
        with pytest.raises(ValueError):
            self.field = 3


class TestClientIDsField:
    field = api.ClientIDsField(required=True, nullable=False)

    def test_ok(self):
        self.field = [1, 2, 3, 4]
        assert self.field == [1, 2, 3, 4]

    def test_incorrect_type(self):
        with pytest.raises(TypeError):
            self.field = '1'

    def test_empty_list(self):
        with pytest.raises(ValueError):
            self.field = []

    def test_incorrect_value(self):
        with pytest.raises(ValidationError):
            self.field = [1, '2', 3, 'a']


if __name__ == "__main__":
    pytest.main()
