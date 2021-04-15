
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse

from tags.models import Tag
from users.models import UserAccount
from ..models import Question, Answer

from .model_test_data import mock_questions_submitted


class TestTopQuestionsPageBadQueryString(TestCase):
    '''Verify that when a "tab" query string argument doesn\'t
    match of any lookup filters that the default is "interesting"'''
    pass

    @classmethod
    def setUpTestData(cls):
        cls.url_path = reverse('questions:mainpage')
        anchor = f'<a href={cls.url_path}?tab=interesting>Interesting</a>'
        cls.button = f"<li class='active lookup_btn'>{anchor}</li>"

    def test_top_questions_url_query_string_filter(self):
        response = self.client.get(f"{self.url_path}?tab=abc123")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "questions/top_questions.html")
        self.assertContains(response, self.button, html=True)


class TestTopQuestionsPageInterestingLookUp(TestCase):
    '''Verify that the questions displayed on the page only have tags
    similiar to the tags submitted along with the questions 
    that a User has posted.'''

    @classmethod
    def setUpTestData(cls):
        tag1 = Tag.objects.create(name="tag1")
        tag2 = Tag.objects.create(name="tag2")
        tag3 = Tag.objects.create(name="tag3")
        tag4 = Tag.objects.create(name="tag4")
        cls.user1 = User.objects.create_user("Me")
        user1_account = UserAccount.objects.create(user=cls.user1)
        user2 = User.objects.create_user("MockUser1")
        user2_account = UserAccount.objects.create(user=user2)
        user3 = User.objects.create_user("MockUser2")
        user3_account = UserAccount.objects.create(user=user3)

        for i, q in enumerate(mock_questions_submitted):
            if i == 0:
                q.update(user_account=user1_account)
                question = Question.objects.create(**q)
                question.tags.add(tag1)
            elif i == 1:
                q.update(user_account=user3_account)
                question = Question.objects.create(**q)
                question.tags.add(tag2, tag3, tag4)
            else:
                q.update(user_account=user2_account)
                question = Question.objects.create(**q)
                question.tags.add(tag1, tag2)

    def test_top_questions_filtered_with_interesting_lookup(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('questions:mainpage'))
        self.assertTemplateUsed("questions/top_questions.html")
        self.assertNotContains(response, 'tag3')
        self.assertNotContains(response, 'tag4')
