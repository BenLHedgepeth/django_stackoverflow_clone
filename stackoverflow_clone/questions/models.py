from datetime import date, timedelta

from django.db import models
from tags.models import Tag

import markdown

class DateRangeQuerySet(models.QuerySet):

    def week_long(self):
        today = date.today()
        week_ago = today - timedelta(days=7)
        return (self.filter(dated__range=(week_ago, today))
                    .prefetch_related("tags")[:10])

    def month_long(self):
        today = date.today()
        month_ago = today - timedelta(days=30)
        return (self.filter(dated__range=(month_ago, today))
                    .prefetch_related("tags")[:10])

    def recent(self):
        today = date.today()
        recently = today - timedelta(days=3)
        return (self.filter(dated__range=(recently, today))
                    .prefetch_related("tags")[:10])


class QuestionStatusQuerySet(models.QuerySet):

    def unanswered(self):
        return self.filter(answers__isnull=True)

    def newest(self):
        return self.order_by('-dated')


class QuestionVote(models.Model):
    vote = models.CharField(max_length=7)
    account = models.ForeignKey(
        'users.UserAccount',
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name="votes"
    )


class Question(models.Model):
    title = models.CharField(max_length=50)
    body = models.TextField()
    dated = models.DateField(default=date.today)
    user_account = models.ForeignKey(
        'users.UserAccount',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="questions"
    )
    tags = models.ManyToManyField(Tag, related_name='questions')

    objects = models.Manager()
    dateranges = DateRangeQuerySet.as_manager()
    status = QuestionStatusQuerySet.as_manager()

    class Meta:
        ordering = ['-dated']
        default_manager_name = "objects"

    def __str__(self):
        return self.title


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    response = models.TextField()
    dated = models.DateField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    user_account = models.ForeignKey(
        'users.UserAccount',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="answers"
    )

    class Meta:
        ordering = ['-likes']
