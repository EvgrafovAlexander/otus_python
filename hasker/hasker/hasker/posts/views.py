from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import generic

from .forms import AddAnswerForm, AddQuestionForm, RegisterUserForm
from .models import Answer, AnswerVote, Question, QuestionVote


# Create your views here.
class IndexViewLast(generic.ListView):
    template_name = "posts/index.html"
    context_object_name = "latest_question_list"
    paginate_by = 2

    def get_queryset(self):
        """
        Получить набор из вопросов, сортированных по дате публикации

        lte = меньше или равно
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")


class IndexViewHot(generic.ListView):
    template_name = "posts/index.html"
    context_object_name = "latest_question_list"
    paginate_by = 2

    def get_queryset(self):
        """
        Получить набор из вопросов, сортированных по дате публикации

        lte = меньше или равно
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-votes")


class SearchResultsList(generic.ListView):
    model = Question
    context_object_name = "latest_question_list"
    template_name = "posts/index.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        return Question.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query) | Q(title__iexact=query) | Q(text__iexact=query)
        ).order_by("-votes", "-pub_date")


def question_view(request, pk):
    question = get_object_or_404(Question, pk=pk)
    question.already_vote = QuestionVote.objects.filter(question=question).exists()
    answers = Answer.get_answers(question)
    return render(request, "posts/detail.html", {"question": question, "answers": answers})


def register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                print("Сохранение пользователя")
                print(form.cleaned_data)
                new_user = form.save(commit=False)
                new_user.email = form.cleaned_data["email"]
                new_user.avatar = form.cleaned_data["avatar"]
                new_user.save()
                return redirect("posts:login")
            except Exception as e:
                print(e)
                form.add_error(None, "Не удалось добавить пользователя")
    else:
        form = RegisterUserForm()
    return render(request, "posts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("posts:index")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="posts/login.html", context={"login_form": form})


def add_question(request):
    if request.method == "POST":
        form = AddQuestionForm(request.POST)
        if form.is_valid():
            try:
                question = form.save(commit=False)
                question.author = request.user
                question.save()
                form.save_m2m()
                return redirect("posts:detail", pk=question.id)
            except Exception as e:
                print(e)
                form.add_error(None, "Не удалось добавить вопрос")
    else:
        form = AddQuestionForm()
    return render(request, "posts/add_question.html", {"form": form})


def add_answer(request, pk):
    if request.method == "POST":
        form = AddAnswerForm(request.POST)
        if form.is_valid():
            try:
                print("Сохранение ответа")
                answer = form.save(commit=False)
                answer.author = request.user
                answer.question_id = pk
                answer.save()
                return redirect("posts:detail", pk=pk)
            except Exception as e:
                print(e)
                form.add_error(None, "Не удалось добавить вопрос")
    else:
        form = AddAnswerForm()
    return render(request, "posts/add_answer.html", {"form": form, "pk": pk})


def change_answer_rate(request):
    pk_question = request.POST.get("question_id")
    pk_answer = request.POST.get("answer_id")
    vote = int(request.POST.get("vote"))

    question = get_object_or_404(Question, pk=pk_question)
    question.already_vote = QuestionVote.objects.filter(question=question).exists()
    answer = get_object_or_404(Answer, pk=pk_answer)
    already_vote = AnswerVote.objects.filter(user=request.user).filter(answer=answer)
    if not already_vote:
        votes = answer.votes + vote
        is_plus = vote == 1
        Answer.objects.filter(pk=pk_answer).update(votes=votes)
        # Добавляем информацию о голосовании пользователя
        vote = AnswerVote(user=request.user, answer=answer, is_plus=is_plus)
        vote.save()
    else:
        messages.error(request, "Для повторного голосования отмените свой голос.")
    answers = Answer.get_answers(question)
    return render(request, "posts/detail.html", {"question": question, "answers": answers})


def change_question_rate(request):
    pk_question = request.POST.get("question_id")
    vote = int(request.POST.get("vote"))

    question = get_object_or_404(Question, pk=pk_question)
    question.already_vote = QuestionVote.objects.filter(question=question).exists()
    already_vote = QuestionVote.objects.filter(user=request.user).filter(question=question)
    if not already_vote:
        votes = question.votes + vote
        is_plus = vote == 1
        Question.objects.filter(pk=pk_question).update(votes=votes)
        # Добавляем информацию о голосовании пользователя
        vote = QuestionVote(user=request.user, question=question, is_plus=is_plus)
        vote.save()
    else:
        messages.error(request, "Для повторного голосования отмените свой голос.")
    answers = Answer.get_answers(question)
    return render(request, "posts/detail.html", {"question": question, "answers": answers})


def choose_the_best(request, pk_question, pk_answer):
    """Выбрать наилучший ответ"""
    Question.objects.filter(pk=pk_question).update(found_answer=True)
    Answer.objects.filter(pk=pk_answer).update(is_right=True)
    question = get_object_or_404(Question, pk=pk_question)
    question.already_vote = QuestionVote.objects.filter(question=question).exists()
    answers = Answer.get_answers(question)
    return render(request, "posts/detail.html", {"question": question, "answers": answers})


def cancel_answer_vote(request):
    pk_question = request.POST.get("question_id")
    pk_answer = request.POST.get("answer_id")

    votes = AnswerVote.objects.filter(user=request.user).filter(answer_id=pk_answer)
    roll_vote = 1 if votes[0].is_plus else -1
    votes.delete()
    answer = get_object_or_404(Answer, pk=pk_answer)
    votes_update = answer.votes - roll_vote
    Answer.objects.filter(pk=pk_answer).update(votes=votes_update)

    question = get_object_or_404(Question, pk=pk_question)
    answers = Answer.get_answers(question)
    return render(request, "posts/detail.html", {"question": question, "answers": answers})


def cancel_question_vote(request):
    pk_question = request.POST.get("question_id")

    votes = QuestionVote.objects.filter(user=request.user).filter(question_id=pk_question)
    roll_vote = 1 if votes[0].is_plus else -1
    votes.delete()
    question = get_object_or_404(Question, pk=pk_question)
    votes_update = question.votes - roll_vote
    Question.objects.filter(pk=pk_question).update(votes=votes_update)

    question = get_object_or_404(Question, pk=pk_question)
    answers = Answer.get_answers(question)
    return render(request, "posts/detail.html", {"question": question, "answers": answers})
