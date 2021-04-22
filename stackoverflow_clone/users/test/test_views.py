
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user

class TestRegisterPageSuccessRedirect(TestCase):
    '''Verify that a User is redirected to a login page
    after successfully registering.'''

    @classmethod
    def setUpTestData(cls):
        cls.previous_register_user_count = 0

    def test_register_user_redirect_to_login_pass(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "username": "TestUser1",
                "password1": "mysecret*code",
                "password2": "mysecret*code"
            }
        )
        current_user_register_count = User.objects.count()

        self.assertTrue(
            current_user_register_count > self.previous_register_user_count
        )
        self.assertTemplateUsed("users/register_user.html")
        self.assertRedirects(
            response, reverse("users:login"), status_code=303
        )


class TestLoginUserFormRedirectToNext(TestCase):
    '''Verify that a User is redirected to the login_required page
    after providing their credentials to login.'''

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user("Me", password="secret*code")
        cls.data = {
            'username': 'Me',
            'password': 'secret*code'
        }
        cls.url = reverse("questions:mainpage")

    def test_login_redirect_next_pass(self):
        response = self.client.post(
            reverse("users:login"),
            data=self.data,
            follow=True,
            HTTP_REFERER=self.url
        )
        user = get_user(self.client)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(response.resolver_match.route, '')
        self.assertTemplateUsed(response, "questions/top_questions.html")
        self.assertContains(response, "Profile")
        self.assertContains(response, "Log Out")



class TestLoginUserFormFailed(TestCase):
    '''Verify that a User is redirected back to the login page
    with a failed attempt to login.'''

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user("Me", password="secret*code")
        cls.data = {
            'username': 'Me',
            'password': 'secret*de'
        }
        cls.url = f"{reverse('questions:mainpage')}?tab=interesting"

    def test_login_redirect_next_back_to_login(self):
        response = self.client.post(
            reverse("users:login"),
            data=self.data,
            follow=True,
            HTTP_REFERER=self.url
        )
        user = get_user(self.client)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(user.is_authenticated)
        self.assertTemplateUsed(response, "users/login_page.html")
