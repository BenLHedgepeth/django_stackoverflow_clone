from django.test import TestCase
from django.contrib.auth.models import User

from ..forms import QuestionForm, Question, SearchForm
from tags.models import Tag
from users.models import UserAccount


class TestQuestionFormClean(TestCase):
    '''Verify that a User cannot submit their question when
    a question already exists with the supplied tags'''

    @classmethod
    def setUpTestData(cls):
        tag1 = Tag.objects.create(name="tag1")
        tag2 = Tag.objects.create(name="tag2")
        user = User.objects.create_user("Me")
        user_account = UserAccount.objects.create(user=user)
        data = {
            'title': "How do I render CSS files with Django?",
            'body': "No CSS is rendering in my project",
            'user_account': user_account,
        }
        question = Question.objects.create(**data)
        question.tags.add(tag1, tag2)
        data['tags'] = [tag1]
        cls.question_form = QuestionForm(data)
        cls.question_body_errors = cls.question_form.errors.as_data()['body']

    def test_error(self):
        message = "A question like this already exists."
        message += " Reformat your question and/or change your tags."
        self.assertTrue(
            any(filter(
                lambda error: error.message == message,
                self.question_body_errors
            ))
        )


class TestQuestionTagsField(TestCase):
    '''Verify that a User cannot submit a question with more than 4 tags'''

    @classmethod
    def setUpTestData(cls):
        tags = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5']
        tag1, tag2, tag3, tag4, tag5 = [
            Tag.objects.create(name=tag) for tag in tags
        ]
        user = User.objects.create_user("Me")
        user_account = UserAccount.objects.create(user=user)
        data = {
            'title': "",
            'body': "",
            'user_account': user_account,
            'tags': [tag1, tag2, tag3, tag4, tag5]
        }
        question_form = QuestionForm(data)
        cls.question_form_tags_error = question_form.errors.as_data()['tags']

    def test_question_tag_limit_exceeded(self):
        self.assertTrue(any(
            error.message == "Only attach a maximum of 4 tags."
            for error in self.question_form_tags_error
        ))


class TestQuestionCreated(TestCase):
    '''Verify that a Question is created when no form errors are present.'''
    pass


class TestSearchForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        form = SearchForm()
        cls.search_form_attrs = form.fields['search'].widget.attrs

    def test_search_form_placeholder(self):
        self.assertEqual(
            self.search_form_attrs['placeholder'],
            "Search..."
        )
