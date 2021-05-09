

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse


from ..models import QuestionVote, Question
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
        self.assertEqual(response.data['vote'][0], "You have already voted")


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

    def test_user_change_vote(self):
        self.client.login(username="Me", password="topsecretcode")
        for i in range(2):
            response = self.client.put(
                reverse("questions_api:vote", kwargs={'id': 1}),
                data={"vote": self.votes[i]}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['tally'], 0)

    def test_user_add_downvote(self):
        self.client.login(username="Me", password="topsecretcode")
        response = self.client.put(
            reverse("questions_api:vote", kwargs={'id': 1}),
            data={"vote": self.votes[1]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['tally'], -1)

    def test_user_add_upvote(self):
        self.client.login(username="Me", password="topsecretcode")
        response = self.client.put(
            reverse("questions_api:vote", kwargs={'id': 1}),
            data={"vote": self.votes[0]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['tally'], 1)

#
# class TestUserVoteOnOwnQuestion(APITestCase):
#     '''Verify that a User cannot vote on their own Question'''
#
#     @classmethod
#     def setUpTestData(cls):
#         cls.user1 = User.objects.create_user("Me", password="topsecretcode")
#         cls.user1_account = UserAccount.objects.create(user=cls.user1)
#         cls.tag = Tag.objects.create(name="Tag")
#         cls.q = mock_questions_submitted[2]
#         cls.q.update({'user_account': cls.user1_account})
#         cls.question = Question(**cls.q)
#         cls.question.save()
#         cls.question.tags.add(cls.tag)
#
#     def test_vote_on_own_posted_question(self):
#         self.client.login(username="Me", password="topsecretcode")
#         response = self.client.put(
#             reverse("questions_api:vote", kwargs={'id': 1}),
#             data={"vote": "upvote"}
#         )
#         self.assertEqual(response.status_code, 400)
#         self.assertEquals(
#             response.data['votes'][0],
#             "You cannot vote on your question"
#         )
