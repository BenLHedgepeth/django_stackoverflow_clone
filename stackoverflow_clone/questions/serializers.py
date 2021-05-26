
from django.core.exceptions import ValidationError

from .models import QuestionVote, AnswerVote, Question

from rest_framework import serializers

class VoteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    vote = serializers.CharField(write_only=True)

    def validate_vote(self, value):
        if self.instance and (value == self.instance.vote):
            raise ValidationError("Duplicate vote not allowed", code="vote_error")
        return value


class QuestionVoteSerializer(VoteSerializer):


    def create(self, validated_data):
        return QuestionVote.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.vote = validated_data.get('vote', instance.vote)
        instance.save()
        return instance




class AnswerVoteSerializer(VoteSerializer):


    def create(self, *args, **kwargs):
        return AnswerVote.objects.create(*args, **kwargs)
