from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

from ..forms import RegisterUserForm
from ..validators import SameCharacterPasswordValidator

class TestInfiniteCharacterValidator(TestCase):
    '''Verify that an error is raised when the password
    supplied contains the same character.'''

    @classmethod
    def setUpTestData(cls):
        cls.invalid_password = "AAAAAAAA"
        cls.password_validator = SameCharacterPasswordValidator()


    def test_password_supplied_has_same_characters(self):
        with self.assertRaises(ValidationError):
            self.password_validator.validate(self.invalid_password)


class TestRegisterUserForm(TestCase):
    '''Verify that a User's password triggers SameCharacterPasswordValidator
    when the User attempts to register an account.'''

    @classmethod
    def setUpTestData(cls):
        data = {
            'username': "TestUser",
            'password1': "ZZZZZZZ",
            'password2': "ZZZZZZZ"
        }
        cls.register_form = RegisterUserForm(data)
        cls.password_errors = cls.register_form.errors.as_data()['password2']

    def test_password_character_validator_fail(self):
        message = "Password cannot entirely consist of the same character"
        self.assertFalse(self.register_form.is_valid())
        self.assertTrue(any(
            error.message == message for error in self.password_errors
        ))
