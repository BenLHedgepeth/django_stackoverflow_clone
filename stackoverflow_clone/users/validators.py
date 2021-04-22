from django.core.exceptions import ValidationError


class SameCharacterPasswordValidator:

    def validate(self, password, user=None):
        if all(password[i] == password[i + 1] for i in range(len(password) - 1)):
            raise ValidationError(
                "Password cannot entirely consist of the same character"
            )

    def get_help_text(self):
        return "Provide a password that has at least two distinct characters"
