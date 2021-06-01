
from django.conf import settings
import re

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class NewUserForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label.title()
            field.widget.attrs['class'] = "register_text_widget"



class UserLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label.title()
            field.widget.attrs['class'] = "login_text_widget"
