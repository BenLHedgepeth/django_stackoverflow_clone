from django.views.generic.base import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.urls import reverse
from django.contrib import messages
from .forms import RegisterUserForm, LoginUserForm

from .codes import HttpResponseSeeOther

class RegisterPage(TemplateView):

    template_name = "users/register_user.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['register_form'] = RegisterUserForm(self.request.POST or None)
        return context

    def get(self, request):
        context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, request):
        context = self.get_context_data()
        if context['register_form'].is_valid():
            context['register_form'].save()
            messages.success(request, "You're registered! Please login!")
            return HttpResponseSeeOther(reverse("users:login"))
        return self.render_to_response(context)


class LoginPage(TemplateView):

    template_name = "users/login_page.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['login_form'] = LoginUserForm(data=self.request.POST or None)
        return context

    def get(self, request):
        context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, request):
        context = self.get_context_data()
        form = context['login_form']
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseSeeOther(reverse("questions:mainpage"))
        return self.render_to_response(context)


def logout_user(request):
    import pdb; pdb.set_trace()
    logout(request)
    return HttpResponseSeeOther(reverse("users:login"))
