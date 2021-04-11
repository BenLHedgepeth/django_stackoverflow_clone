from datetime import date

from django.db import models
from tags.models import Tag

# Create your models here.
class Question(models.Model):
    title = models.CharField(unique=True, max_length=50)
    body = models.TextField()
    dated = models.DateField(default=date.today)
    likes = models.IntegerField(default=0)
    user_account = models.ForeignKey(
        'users.UserAccount',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="questions"
    )
    tags = models.ManyToManyField(Tag, related_name='questions')

    class Meta:
        ordering = ['dated']


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
