"""stackoverflow_clone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from questions import views as qv
from users import views as uv
from tags import views as tv


question_urls = ([
    path("", qv.TopQuestionsPage.as_view(), name="mainpage"),
    path("questions/", qv.AllQuestionsPage.as_view(), name="paginated"),
    path("questions/create/", qv.PostQuestionPage.as_view(), name="create"),
    path("questions/<id>/", qv.UserQuestionPage.as_view(), name="question")
], 'questions')
user_urls = ([
    path("register/", uv.RegisterPage.as_view(), name="register"),
    path("login/", uv.LoginPage.as_view(), name="login"),
    path("logout/", uv.logout_user, name="logout")
], 'users')
# tag_urls = ([
#
# ], 'tags')


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(question_urls)),
    path("users/", include(user_urls)),
]
