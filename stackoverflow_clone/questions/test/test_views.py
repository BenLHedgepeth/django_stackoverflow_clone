
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
        cls.user = User.objects.create_user("Me")
        cls.url_path = reverse('questions:mainpage')
        anchor = f'<a href={cls.url_path}?tab=interesting>Interesting</a>'
        cls.button = f"<li class='active lookup_btn'>{anchor}</li>"

    def test_top_questions_url_query_string_filter(self):
        self.client.force_login(self.user)
        response = self.client.get(f"{self.url_path}?tab=abc123")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "questions/top_questions.html")
        self.assertContains(response, self.button, html=True)


class TestTopQuestionsPageInterestingLookUp(TestCase):
    '''Verify that the questions displayed on the page only have tags
    similiar to the tags attached to the questions
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
                q.update({'user_account': user3_account})
                q.pop('tags')
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


class TestAllQuestionsPageInvalidPage(TestCase):
    '''Verify that a User is sent to Page #1 of a
    paginated set of questions when they search for
    a page that falls outside the possible range of pages'''

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Me")
        user_account = UserAccount.objects.create(user=cls.user)
        cls.url = reverse("questions:paginated")

    def test_paginated_questions_default_page_number(self):
        self.client.force_login(self.user)
        response = self.client.get(f"{self.url}?page=111111111111111")
        self.assertTemplateUsed("questions/all_questions.html")
        self.assertContains(
            response,
            "Page 1",
        )


class TestAllQuestionsPageValidPage(TestCase):
    pass


class TestPostQuestionPageSameQuestion(TestCase):
    '''Verify that a User receives an error message indicating
    that a Question exists with the provided tags.'''

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Me")
        account = UserAccount.objects.create(user=cls.user)
        python_tag = Tag.objects.create(name="Python")
        cls.data = mock_questions_submitted[0]
        cls.data.update({'user_account': account})
        question = Question.objects.create(**cls.data)
        question.tags.add(python_tag)
        cls.previous_question_total = Question.objects.count()

        cls.submitted_data = cls.data.copy()
        cls.submitted_data.pop('user_account')
        cls.submitted_data.update({'tags': [python_tag]})

    def test_invalid_question_submission_duplicate_question(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("questions:create"),
            data=self.submitted_data
        )
        current_question_total = Question.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/create_question.html')
        self.assertContains(response, "A question like this already exists. Reformat your question and/or change your tags.")
        self.assertEqual(self.previous_question_total, current_question_total)


class TestPostQuestionPageAdded(TestCase):
    '''Verify that a User has succesfully added a question'''

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Me")
        cls.account = UserAccount.objects.create(user=cls.user)
        tag1 = Tag.objects.create(name="tag1")
        tag2 = Tag.objects.create(name="tag2")
        cls.data = mock_questions_submitted[1]
        cls.data.update(
            {'tags': [tag1, tag2]}
        )

    def test_user_submitted_question_added(self):
        total_questions = Question.objects.count()
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("questions:create"),
            data=self.data,
        )
        question = Question.objects.all().get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(question.user_account, self.account)


class TestQuestionPageListed(TestCase):
    '''Verify that the Question submitted by a User
    can be viewed by other Users.'''

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Me")
        cls.user_account = UserAccount.objects.create(user=cls.user)
        cls.tag1 = Tag.objects.create(name="Tag1")
        cls.data = mock_questions_submitted[2]
        cls.data.update({'user_account': cls.user_account})
        cls.question = Question.objects.create(**cls.data)
        cls.question.tags.add(cls.tag1)

    def test_user_question_listed_on_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse(
            "questions:question", kwargs={'id': 1}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "questions/question.html")
        self.assertContains(response, 'What are Python decorators use cases?')
        self.assertContains(response, "Edit")
        self.assertContains(response, "Delete")
        self.assertContains(response, "Tag1")
        self.assertContains(response, "Me")
        self.assertContains(response, "Provide your answer here")


class TestQuestionEditPage(TestCase):
    '''Verify that a User is able to edit a Question that is already
    posted.'''

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Me")
        cls.account = UserAccount.objects.create(user=cls.user)
        cls.tag = Tag.objects.create(name="Tag3")
        cls.new_tag = Tag.objects.create(name="Tag2")
        cls.question = mock_questions_submitted[3]
        cls.question.update({'user_account': cls.account})
        cls.posted_question = Question.objects.create(**cls.question)
        cls.posted_question.tags.add(cls.tag)

    def test_question_posted_changed(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("questions:question_edit", kwargs={'id': 1}),
            data={
                'title': "Why does the filter method return a filter object and not a list?",
                'tags': [self.new_tag]
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "questions/question_edit.html")
        self.assertContains(
            response,
            "Why does the filter method return a filter object and not a list?"
        )
        self.assertContains(response, "Tag2")
