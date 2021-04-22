
from unittest.mock import Mock, patch
from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Question, Answer
from tags.models import Tag
from users.models import UserAccount

from .model_test_data import mock_questions_submitted


class TestQuestionDateRangeQuerySet(TestCase):
    '''Verify that each queryset method filters
    all questions in the database by a prescribed
    date time delta'''

    @classmethod
    def setUpTestData(cls):
        tag1 = Tag.objects.create(name="tag1")
        user = User.objects.create_user("User")
        user_account = UserAccount.objects.create(user=user)
        cls.qs = {}
        for q in mock_questions_submitted:
            q.update({'user_account': user_account})
            question = Question.objects.create(**q)
            question.tags.add(tag1)
            cls.qs.update({f'q{question.pk}': question})

    def test_questions_posted_week_ago(self):
        with patch('questions.models.date') as mock_date:
            mock_date.today = Mock(return_value=date(2021, 3, 13))
            week_old_questions = Question.dateranges.week_long()
            self.assertEqual(week_old_questions.count(), 2)
            self.assertQuerysetEqual(
                week_old_questions,
                map(repr, [self.qs['q1'], self.qs['q2']])
            )

    def test_questions_posted_month_ago(self):
        with patch('questions.models.date') as mock_date:
            mock_date.today = Mock(return_value=date(2021, 3, 13))
            week_old_questions = Question.dateranges.month_long()
            self.assertEqual(week_old_questions.count(), 4)
            self.assertQuerysetEqual(
                week_old_questions,
                map(repr, [
                    self.qs['q1'], self.qs['q2'], self.qs['q3'], self.qs['q4']
                ])
            )

    def test_questions_posted_recently(self):
        with patch('questions.models.date') as mock_date:
            mock_date.today = Mock(return_value=date(2021, 3, 14))
            week_old_questions = Question.dateranges.recent()
            self.assertEqual(week_old_questions.count(), 1)
            self.assertQuerysetEqual(
                week_old_questions,
                map(repr, [
                    self.qs['q1']
                ])
            )


class TestQuestionStatusQuerySet(TestCase):
    '''Verify that the QuerySets of the QuestionStatus manager
    respectively return all Questions that are either answered
    or unanswered'''

    @classmethod
    def setUpTestData(cls):
        tag = Tag.objects.create(name="tag")
        user = User.objects.create_user("Me")
        other_user = User.objects.create_user("Other")

        user_account = UserAccount.objects.create(user=user)
        other_user_account = UserAccount.objects.create(user=other_user)

        submitted_questions = []
        for i, q in enumerate(mock_questions_submitted):
            q.update(user_account=user_account)
            question = Question.objects.create(**q)
            question.tags.add(tag)
            submitted_questions.append(question)
        cls.q1, cls.q2, cls.q3, cls.q4 = submitted_questions

        answer_data = {
            'question': cls.q2,
            'response': '''
                The purpose of a Primary Key is to mantain uniqueness
                among all records stored in a database table. This is
                is to maintain data integrity and prevent any conflicts
                when it comes to CRUD operations.
            ''',
            'user_account': other_user_account
        }

        answer = Answer.objects.create(**answer_data)
        cls.unanswered_questions = Question.status.unanswered()

    def test_question_status_unanswered_queryset(self):
        self.assertEqual(self.unanswered_questions.count(), 3)
        self.assertQuerysetEqual(
            self.unanswered_questions,
            [self.q1, self.q3, self.q4],
            transform=lambda x: x
        )
