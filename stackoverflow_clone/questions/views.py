
from functools import reduce

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.core.paginator import Paginator, EmptyPage
from .models import Question, Answer
from .forms import SearchForm, QuestionForm, AnswerForm

import markdown

from codes import HttpResponseSeeOther

class QuestionPage(TemplateView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search_form'] = SearchForm()
        return context


class TopQuestionsPage(QuestionPage):
    template_name = "questions/top_questions.html"

    extra_context = {
        'page_title': "Top Questions"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lookup_buttons'] = {
            'interesting': False,
            'hot': False,
            'week': False,
            'month': False,
        }
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
            context['lookup_buttons'].update({f'{lookup}': True})
            if lookup == 'hot':
                questions = Question.dateranges.recent()
            elif lookup == 'week':
                questions = Question.dateranges.week_long()
            else:
                questions = Question.dateranges.month_long()
            context['questions'] = questions
        return self.render_to_response(context)


class AllQuestionsPage(QuestionPage):

    template_name="questions/paginated_questions.html"

    extra_context = {
        'page_title': 'All Questions',
        'lookup_buttons': {
            'newest': False,
            'unanswered': False,
        }
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("tab", None)
        if query == "unanswered":
            context['lookup_buttons'].update(unanswered=True)
            context['questions'] = Question.status.unanswered()
            context['query'] = 'unanswered'
        else:
            context['lookup_buttons'].update(newest=True)
            context['questions'] = Question.status.newest()
            context['query'] = 'newest'
        return context

    def get(self, request):
        context = self.get_context_data()
        p = Paginator(context['questions'], 5)
        query_page = request.GET.get('page', None)
        if query_page:
            try:
                page = p.page(query_page)
            except EmptyPage:
                page = p.page(1)
            finally:
                context['page'] = page
        context['page'] = p.page(1)
        return self.render_to_response(context)


class PostQuestionPage(QuestionPage):

    template_name="questions/create_question.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['question_form'] = QuestionForm(self.request.POST or None)
        return context


    def get(self, request):
        context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, request):
        context = self.get_context_data()
        form = context['question_form']
        if form.is_valid():
            question = form.save(commit=False)
            question.user_account = request.user.account
            question.save()
            form.save_m2m()
            return HttpResponseRedirect(
                reverse("questions:question", kwargs={'id': question.id})
            )
        return self.render_to_response(context)


class UserQuestionPage(QuestionPage):

    template_name = "questions/question.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['answer_form'] = AnswerForm(self.request.POST or None)
        return context

    def get(self, request, id):
        context = self.get_context_data()
        context['question'] = get_object_or_404(Question, id=id)
        return self.render_to_response(context)

    def post(self, request, id):
        context = self.get_context_data()
        context['question'] = get_object_or_404(Question, id=id)
        if context['answer_form'].is_valid():
            response = context['answer_form'].cleaned_data['response']
            question = Question.objects.get(id=id)
            user_account = request.user.account
            answer = Answer.objects.create(
                question=question,
                response=response,
                user_account=user_account
            )
            return HttpResponseRedirect(
                reverse("questions:question", kwargs={'id': id})
            )
        return self.render_to_response(context)


class UserEditQuestionPage(QuestionPage):

    template_name = "questions/question_edit.html"

    extra_context = {
        'page_title': "Edit You Question"
    }

    def get(self, request, id):
        context = self.get_context_data()
        posted_question = get_object_or_404(Question, id=id)
        context['question_form'] = QuestionForm(instance=posted_question)
        return self.render_to_response(context)

    def post(self, request, id):
        context = self.get_context_data()
        posted_question = get_object_or_404(Question, id=id)
        form = QuestionForm(request.POST, instance=posted_question)
        if form.is_valid():
            form.save()
            if form.has_changed():
                messages.info(request, "Question is updated")
            return HttpResponseSeeOther(
                reverse("questions:question", kwargs={'id': id})
            )
        context['question_form'] = form
        return self.render_to_response(context)


class UserEditAnswerPage(QuestionPage):

    template_name = "questions/question.html"

    def get(self, request, q_id, a_id):
        context = super().get_context_data()
        context['question'] = get_object_or_404(Question, id=q_id)
        context['answer'] = get_object_or_404(Answer, id=a_id)
        context['answer_form'] = AnswerForm(instance=context['answer'])
        return self.render_to_response(context)

    def post(self, request, q_id, a_id):
        context = super().get_context_data()
        instance = get_object_or_404(Answer, id=a_id)
        form = AnswerForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseSeeOther(reverse(
                "questions:question", kwargs={'id': q_id})
            )
        context['answer_form'] = form
        return self.render_to_response(context)
