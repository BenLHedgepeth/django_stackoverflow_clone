
from functools import reduce


from django.views.generic.base import TemplateView
from .models import Question


# Create your views here.

class TopQuestionsPage(TemplateView):
    template_name = "questions/top_questions.html"

    extra_context = {
        'lookup_buttons': {
            'interesting': False,
            'hot': False,
            'week': False,
            'month': False,
        }
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = Question.objects.all()
        return context


    def get(self, request):
        context = self.get_context_data()
        lookup = request.GET.get('tab', 'interesting')
        if lookup not in context['lookup_buttons'].keys() or lookup == "interesting":
            user_questions = (
                Question.objects.filter(user_account_id=request.user.id)
                .prefetch_related("tags")
            )
            user_tags = set(
                [tag for question in user_questions
                        for tag in question.tags.all()]
            )
            for tag in user_tags:
                context['questions'] = Question.objects.filter(tags__name=tag)
            context['lookup_buttons'].update(interesting=True)
        else:
            context['lookup_buttons'].update(lookup=True)
            if lookup == 'hot':
                questions = Question.dateranges.recent()
            elif lookup == 'week':
                questions = Question.dateranges.week_long()
            else:
                questions = Question.dateranges.month_long()
            context['questions'] = questions
        return self.render_to_response(context)
