
from unittest.mock import Mock, patch
from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Question
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
