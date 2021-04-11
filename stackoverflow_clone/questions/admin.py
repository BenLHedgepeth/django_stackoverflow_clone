from django.contrib import admin
from .models import Question, Answer
# Register your models here.

class QuestionAdmin(admin.ModelAdmin):
    empty_value_display = "N/A"
    actions_selection_counter = False
    fieldsets = [(
        None, {
            'fields': ('title', 'body', 'tags', 'likes', 'user_account',)
        }
    )]

class AnswerAdmin(admin.ModelAdmin):
    empty_value_display = "--N/A--"
    fields = ['question', 'reply', 'user_account']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
