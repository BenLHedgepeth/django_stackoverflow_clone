
from unitest.mock import Mock
import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Question
from tags.models import Tag
from user.models import UserAccount

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
        for q in mock_questions_submitted:
            q.update({'user_account': user_account})
            question = Question.objects.create(**q)
            question.tags.add(tag1)
        q1, q2, q3, q4 = Question.objects.all()

    def test_questions_posted_week_ago(self):
        with patch('datetime.date.today') as mock_today:
            mock_today = Mock(return_value=datetime.date(2021, 3, 13))
            week_old_questions = Question.dateranges.week()
            self.assert_mock_called_once()
            self.assertEqual(week_old_questions.count(), 2)
            self.assertQuerysetEqual(
                week_old_questions,
                map(repr, [q1, q2])
            )
