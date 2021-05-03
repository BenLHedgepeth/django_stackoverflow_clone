
import re

from django import forms
from django.db.models import Q
from django.core.validators import ValidationError

from tags.models import Tag

from .models import Question, Answer


class QuestionForm(forms.ModelForm):

    css_error_class = "question_form_errors"

    title = forms.CharField(
        widget=forms.TextInput(attrs={
            "autocomplete": "off"
        }),
        help_text="Provide a detailed question for everyone to understand",
        error_messages = {
            'required': "Question must be provided.",
        }
    )

    body = forms.CharField(
        help_text="Give context to better understand your question",
        widget=forms.Textarea(attrs={
            'class': 'body_content',
        }),
        error_messages = {
            'required': "Add some detail about your question"
        }
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        to_field_name="name",

    )

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if tags.count() > 4:
            raise ValidationError(
                "Only attach a maximum of 4 tags.",
                code="tags_limit"
            )
        return tags

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title", None)
        tags = cleaned_data.get("tags", None)
        id = getattr(self.instance, 'id' , None)
        if tags and not id:
            for t in tags:
                try:
                    self.Meta.model.objects.get(
                        title__exact=title, tags__name__exact=t
                    )
                except self.Meta.model.DoesNotExist:
                    continue
                else:
                    message = "A question like this already exists."
                    message += " Reformat your question and/or change your tags."
                    self.add_error("body", ValidationError(
                        message, code="invalid")
                    )


    class Meta:
        model = Question
        fields = ['id', 'title', 'body', 'tags']
        error_messages = {
            'title': {
                'unique': "Question already exists. Reformat your question.",
                'max_length': "Make your question more concise."
            },
            'body': {
                'required': "Specify context around your question",
            }
        }
        help_texts = {
            'title': "Provide a detailed question for everyone to understand",
        }


class AnswerForm(forms.ModelForm):


    response = forms.CharField(
        min_length=50,
        widget=forms.Textarea(),
        error_messages = {
            'min_length': "Your answer must be at least 50 characters long"
        },
        help_text = "Provide your answer here"
    )


    class Meta:
        model = Answer
        fields = ['response']


class SearchForm(forms.Form):

    search = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': "Search...",
            'maxlength': '100',
            'autocomplete': 'off',
            'class': 'search_form'
        })
    )
