
from django.core.exceptions import ValidationError

from .models import QuestionVote, AnswerVote, Question

from rest_framework import serializers

class VoteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    vote = serializers.CharField(write_only=True)

    def validate_vote(self, value):
        vote = value
        if self.instance and (vote == self.instance.vote):
            raise ValidationError("Duplicate vote not allowed", code="vote_error")
        return vote


class QuestionVoteSerializer(VoteSerializer):


    def create(self, validated_data):
        # import pdb; pdb.set_trace()
        return QuestionVote.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.vote = validated_data.get('vote', instance.vote)
        instance.save()
        return instance




class AnswerVoteSerializer(VoteSerializer):

    def create(self, validated_data):
        return AnswerVote.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.vote = validated_data.get('vote', instance.vote)
        instance.save()
        return instance
