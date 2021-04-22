
import re

from django import forms
from django.db.models import Q
from django.core.validators import ValidationError

from tags.models import Tag

from .models import Question

class QuestionForm(forms.ModelForm):
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'body_content',
        })
    )
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all())

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
        if tags:
            for t in tags:
                try:
                    self.Meta.model.objects.get(
                        title__exact=title, tags__name__exact=t
                    )
                except self.Meta.model.DoesNotExist:
                    continue
                else:
                    message = "A question like this already exists."
                    message += "Reformat your question and/or change your tags."
                    self.add_error("body", ValidationError(
                        message, code="invalid")
                    )

    class Meta:
        model = Question
        fields = ['title', 'body', 'tags']
        error_messages = {
            'title': {
                'required': "Question must be provided.",
                'unique': "Question already exists. Reformat your question.",
                'max_length': "Make your question more concise."
            },
            'body': {
                'required': "Specify context around your question",
            }
        }


class SearchForm(forms.Form):

    search = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': "Search...",
            'maxlength': '100',
            'class': 'search_form'
        })
    )
