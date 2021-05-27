
from copy import deepcopy
from unittest.mock import Mock, patch

from django.core.cache import cache
from django.conf import settings
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

REST_FRAMEWORK_TEST = deepcopy(settings.REST_FRAMEWORK)
REST_FRAMEWORK_TEST['DEFAULT_THROTTLE_RATES'] = {"voting": "5555/minute"}

from ..models import QuestionVote, Question, Answer, AnswerVote
from users.models import UserAccount
from tags.models import Tag
from .model_test_data import mock_questions_submitted


class TestQuestionDuplicateUpvote(APITestCase):
    '''Verify that a client is informed that they already
    voted on a question posted.'''

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('Mock', password="mocksecret")
        cls.author = User.objects.create_user("Author")
        cls.user_account = UserAccount.objects.create(user=cls.user)
        cls.author_account = UserAccount.objects.create(user=cls.author)
        q = mock_questions_submitted[0]
        tag = Tag.objects.create(name='Tag')
        q.update({"user_account": cls.author_account})
        cls.question = Question(**q)
        cls.question.save()
        cls.question.tags.add(tag)
        QuestionVote.objects.create(
            vote='upvote', account=cls.user_account, question=cls.question
        )
        cls.old_vote_tally = cls.question.votes.count()

    def test_user_upvote_posted_question(self):
        self.client.login(username="Mock", password="mocksecret")
        response = self.client.put(
            reverse("questions_api:vote", kwargs={"id": 1}),
            data = {'vote': 'upvote'}
        )
        new_vote_tally = self.question.votes.count()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(new_vote_tally, self.old_vote_tally)
        self.assertEqual(response.data['vote'][0], "Duplicate vote not allowed")

class TestQuestionVoteTally(APITestCase):
    '''Verify that the vote tally changes dependent upon
    whether the User has voted previously or not'''

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user("Me", password="topsecretcode")
        cls.user1_account = UserAccount.objects.create(user=cls.user1)
        cls.user2 = User.objects.create_user("Other")
        cls.user2_account = UserAccount.objects.create(user=cls.user2)
        cls.user3 = User.objects.create_user("Other2")
        cls.user3_account = UserAccount.objects.create(user=cls.user3)
        cls.tag = Tag.objects.create(name="Tag")
        cls.q = mock_questions_submitted[2]
        cls.q.update({'user_account': cls.user2_account})
        cls.question = Question(**cls.q)
        cls.question.save()
        cls.question.tags.add(cls.tag)

        cls.votes = ['upvote', 'downvote']

    @override_settings(REST_FRAMEWORK=REST_FRAMEWORK_TEST)
    def test_user_change_vote(self):
        throttle = 'rest_framework.throttling.ScopedRateThrottle'
        with patch(throttle) as mock_throttle:
            self.client.login(username="Me", password="topsecretcode")
            for i in range(2):
                response = self.client.put(
                    reverse("questions_api:vote", kwargs={'id': 1}),
                    data={"vote": self.votes[i]}
                )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['tally'], 0)

    @override_settings(REST_FRAMEWORK=REST_FRAMEWORK_TEST)
    def test_user_add_downvote(self):
        # throttle = 'rest_framework.throttling.ScopedRateThrottle'
        # with patch(throttle) as mock_throttle:
        #     mock_throttle.allow_request = Mock(return_value=True)
        self.client.login(username="Me", password="topsecretcode")
        response = self.client.put(
            reverse("questions_api:vote", kwargs={'id': 1}),
            data={"vote": self.votes[1]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['tally'], -1)

    # @override_settings(REST_FRAMEWORK=REST_FRAMEWORK)
    def test_user_add_upvote(self):
        throttle = 'rest_framework.throttling.ScopedRateThrottle'
        with patch(throttle) as mock_throttle:
            mock_throttle.allow_request = Mock(return_value=True)
            self.client.login(username="Me", password="topsecretcode")
            response = self.client.put(
                reverse("questions_api:vote", kwargs={'id': 1}),
                data={"vote": self.votes[0]}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['tally'], 1)



class TestUserVoteOnOwnQuestion(APITestCase):
    '''Verify that a User cannot vote on their own Question'''

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user("Me", password="topsecretcode")
        cls.user1_account = UserAccount.objects.create(user=cls.user1)
        cls.tag = Tag.objects.create(name="Tag")
        cls.q = mock_questions_submitted[2]
        cls.q.update({'user_account': cls.user1_account})
        cls.question = Question(**cls.q)
        cls.question.save()
        cls.question.tags.add(cls.tag)

    def setUp(self):
        cache.clear()

    def test_vote_on_own_posted_question(self):
        # throttle = 'rest_framework.throttling.ScopedRateThrottle'
        # with patch(throttle) as mock_throttle:
        #     mock_throttle.allow_request = Mock(return_value=True)
        self.client.login(username="Me", password="topsecretcode")
        response = self.client.put(
            reverse("questions_api:vote", kwargs={'id': 1}),
            data={"vote": "upvote"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEquals(
            response.data['vote'],
            "Cannot vote on your own question"
        )

    # def test_user_vote_limit_exceeded(self):
    #     votes = ['upvote', 'downvote', 'upvote', 'downvote', 'upvote', 'dowvote']
    #     self.client.login(username="Me", password="topsecretcode")
    #     for i in range(5):
    #         response = self.client.put(
    #             reverse("questions_api:vote", kwargs={'id': 1}),
    #             data={"vote": votes[i]}
    #         )
    #     self.assertEqual(response.status_code, 429)


class DuplicateAnswerVote(APITestCase):
    '''Verify that a User cannot duplicate the same type of vote
    on a Answer.'''

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Me", password="secretentry")
        cls.user_account = UserAccount.objects.create(user=cls.user)
        cls.answer_author = User.objects.create_user("You")
        cls.author_account = UserAccount.objects.create(user=cls.answer_author)
        cls.tag = Tag.objects.create(name="Tag")
        cls.q = mock_questions_submitted[3]
        cls.q.update({"user_account": cls.user_account})
        cls.question = Question.objects.create(**cls.q)
        cls.question.tags.add(cls.tag)

        response = "dkfdj fd9 jdkf weirj eisldk weurhuehr adjhfdj weirueheksd"
        cls.answer = Answer.objects.create(
            question=cls.question,
            response=response,
            user_account=cls.author_account
        )
        AnswerVote.objects.create(
            vote="downvote",
            answer=cls.answer,
            account=cls.user_account
        )

    @override_settings(REST_FRAMEWORK=REST_FRAMEWORK_TEST)
    def test_reject_duplicate_vote(self):
        throttle = 'rest_framework.throttling.ScopedRateThrottle'
        with patch(throttle) as mock_throttle:
            mock_throttle.allow_request = Mock(return_value=True)
        self.client.login(username="Me", password="secretentry")
        response = self.client.put(
            reverse(
                "questions_api:answer_vote", kwargs={'q_id': 1, 'a_id': 1}
            ), data={"vote": "downvote"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['vote'][0], "Duplicate vote not allowed")


class TestUserVoteOnOwnAnswer(APITestCase):
    '''Verify that an error is raised when a User tries to vote on
    their own answer.'''

    @classmethod
    def setUpTestData(cls):
        cls.tag = Tag.objects.create(name="Tag")
        cls.answer_user = User.objects.create_user("Me", password="secretcode")
        cls.answer_user_account = UserAccount.objects.create(user=cls.answer_user)
        cls.question_user = User.objects.create_user("You")
        cls.question_user_account = UserAccount.objects.create(user=cls.question_user)
        cls.q = mock_questions_submitted[0]
        cls.q.update({"user_account": cls.question_user_account})
        cls.question = Question.objects.create(**cls.q)
        cls.question.tags.add(cls.tag)

        cls.answer = Answer.objects.create(
            question=cls.question,
            response="""
                A reason that a 'NameError' is being raised is due it is
                not declared in the scope that is currently being executed.
            """,
            user_account=cls.answer_user_account
        )

    def test_user_answer_vote_not_allowed(self):
        self.client.login(username="Me", password="secretcode")
        response = self.client.put(
            reverse("questions_api:answer_vote", kwargs={"q_id": 1, "a_id": 1}),
            data={"vote": "upvote"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['vote'], "Cannot vote on own answer")


class TestDeleteUserQuestion(APITestCase):
    '''Verify that a User Question and its associated
    Answers are deleted once the User clicks the delete button
    on the page.'''

    @classmethod
    def setUpTestData(cls):
        cls.tag = Tag.objects.create(name="Tag")
        cls.user = User.objects.create_user("Me", password="TopSecret")
        cls.user_account = UserAccount.objects.craete(user=cls.user)
        cls.answer_user = User.objects.create_user("You")
        cls.answer_user_account = UserAccount.objects.create(user=cls.answer_user)
        cls.q = mock_questions_submitted[1]
        cls.q.update({'user_account': cls.user_account})
        cls.question = Question.objects.create(**q)
        cls.questions.tags.add(cls.tag)

        cls.answer = Answer.objects.create(
            question=cls.question,
            user_account=cls.answer_user_account,
            response="""
                A primary key is used to uniquely identify a individual row
                within a relation for the purpose of CRUD operations.
            """
        )
        cls.previous_total_questions = Question.objects.count()
        cls.previous_question_answers = Question.answers.count()
        cls.previous_total_answers = Question.objects.count()

        def test_delete_posted_question(self):
            self.client.force_authenticte(user=self.user)
            response = self.client.delete(
                reverse("question_api:questions"),
                data={'id': 1}
            )

            current_questions = Question.objects.count()
            question_answers = Question.answers.count()
            answers = Answer.objects.count()

            self.assertEqual(response.status_code, 204)
            self.assertLess(current_questions, self.total_questions)
            self.assertLess(question_answers, self.previous_questions_answers)
            self.assertLess(answers, self.previous_total_answers)


class TestUserAnswerVoteAdded(APITestCase):
    '''Verify that a User can successfully upvote an Answer'''

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Me", password="secretknock")
        cls.user_account = UserAccount.objects.create(user=cls.user)
        
