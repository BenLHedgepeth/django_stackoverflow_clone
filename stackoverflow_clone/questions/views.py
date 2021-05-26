
from functools import reduce
from itertools import chain

from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views import View
from django.views.generic.base import TemplateView
from django.core.paginator import Paginator, EmptyPage
from .models import Question, Answer, QuestionVote, AnswerVote
from .forms import SearchForm, QuestionForm, AnswerForm
from .serializers import QuestionVoteSerializer, AnswerVoteSerializer

import markdown
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response

from codes import HttpResponseSeeOther

from users.models import UserAccount
from tags.models import Tag

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
            context['questions'] = Question.objects.filter(
                        tags__questions__user_account_id=request.user.id,
            )
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

    template_name="questions/paginated_all_questions.html"

    extra_context = {
        'page_title': 'All Questions'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lookup_buttons'] = {
            'newest': False,
            'unanswered': False,
        }
        query = self.request.GET.get("tab", "newest")
        if query not in context['lookup_buttons'].keys() or query == "newest":
            context['lookup_buttons'].update({"newest": True})
            context['questions'] = Question.status.newest()
            context['query'] = 'newest'
        else:
            context['lookup_buttons'].update({"unanswered": True})
            context['questions'] = Question.status.unanswered()
            context['query'] = 'unanswered'
        return context

    def get(self, request):
        context = self.get_context_data()
        print(f"Now: {context['lookup_buttons']}")
        p = Paginator(context['questions'], 5)
        query_page = request.GET.get('page', None)
        if query_page:
            try:
                page = p.page(query_page)
            except EmptyPage:
                page = p.page(1)
            finally:
                context['page'] = page
        else:
            context['page'] = p.page(1)
        context['page'] = p.get_page(query_page)
        print(f"Now: {context['lookup_buttons']}")
        return self.render_to_response(context)


class TaggedQuestionPage(AllQuestionsPage):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, tag):
        context = self.get_context_data()
        context['page_title'] = f"Questions tagged [{tag}]"
        tagged_questions = context['questions'].filter(
            tags__name__icontains=tag.lower()
        )
        if not tagged_questions:
            raise Http404
        p = Paginator(context['questions'], 5)
        query_page = request.GET.get('page', None)
        if query_page:
            try:
                page = p.get_page(query_page)
            except EmptyPage:
                page = p.get_page(1)
            finally:
                context['page'] = page
        else:
            context['page'] = p.get_page(1)
        context['questions'] = tagged_questions
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


class SearchPage(View):

    template_name = "questions/paginated_tagged_questions.html"

    def get(self, request):
        q_param = request.GET.get('q')
        try:
            tag = q_param.strip('[]').title()
            Tag.objects.get(name=tag)
        except Tag.DoesNotExist:
            pass
        else:
            return HttpResponseRedirect(
                reverse("questions:tagged_search", kwargs={'tag': tag.lower()})
            )




class UserQuestionVoteView(APIView):

    # throttle_scope = "voting"

    def put(self, request, id):
        account = UserAccount.objects.get(user=request.user)
        question = get_object_or_404(Question, id=id)
        # r = request.get('placeholder-external-api')
        # if r.status_code == 429:
        #     raise TooManyRequest()
        if account == question.user_account:
            return Response(data={
                'vote': "Cannot vote on your own question"
            }, status=400)
        try:
            stored_vote = QuestionVote.objects.get(
                account=account, question=question
            )
            serializer = QuestionVoteSerializer(stored_vote, request.data)
        except QuestionVote.DoesNotExist:
            serializer = QuestionVoteSerializer(data=request.data)
        finally:
            if serializer.is_valid(raise_exception=True):
                question_vote = serializer.save(
                    account=account,
                    question=question
                )
                vote = serializer.validated_data['vote']
                if vote == "downvote":
                    question.vote_tally = F('vote_tally') - 1
                else:
                    question.vote_tally = F('vote_tally') + 1
                question.save()
                question.refresh_from_db()
                return Response(data={
                    'id': question.id,
                    'tally': question.vote_tally
                }, status=200)

            return Response(serializer.errors, status=400)


class UserAnswerVoteView(APIView):

    throttle_scope = "voting"


    def put(self, request, q_id, a_id):
        question = get_object_or_404(Question, id=q_id)
        answer = get_object_or_404(Answer, id=a_id)
        if answer.user_account.user == request.user:
            return Response(data={"vote": "Cannot vote on own answer"}, status=400)
        account = UserAccount.objects.get(user=request.user)
        try:
            answer_vote = AnswerVote.objects.get(
                account=account,
                answer=answer
            )
            serializer = AnswerVoteSerializer(answer_vote, request.data)
        except AnswerVote.DoesNotExist:
            serializer = AnswerVoteSerializer(data=request.data)
        finally:
            if serializer.is_valid(raise_exception=True):
                vote = serializer.validated_data['vote']
                if vote == "downvote":
                    answer.vote_tally = F('vote_tally') - 1
                else:
                    answer.vote_tally = F('vote_tally') + 1
                answer.save()
                answer.refresh_from_db()
                return Response(data={
                    'id': question.id,
                    'tally': answer.vote_tally
                })
            return Response(serializer.errors)


class QuestionsView(APIView):

    def delete(self, request):
        question = Question.objects.get(id=request.data['id'])
        question.delete()
        return Response(status=204)
