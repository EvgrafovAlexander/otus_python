from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import generic

from .forms import AddQuestionForm, RegisterUserForm
from .models import Question


# Create your views here.
class IndexView(generic.ListView):
    template_name = "posts/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Получить набор из вопросов, сортированных по дате публикации

        lte = меньше или равно
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:20]


class DetailView(generic.DetailView):
    model = Question
    template_name = "posts/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


def register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            try:
                print("Сохранение пользователя")
                print(form.cleaned_data)
                new_user = form.save(commit=False)
                new_user.email = form.cleaned_data["email"]
                new_user.save()
                return redirect("posts:login")
            except Exception as e:
                print(e)
                form.add_error(None, "Не удалось добавить пользователя")
    else:
        form = RegisterUserForm()
    return render(request, "posts/register.html", {"form": form})


def login(request):
    return render(request, "posts/login.html", {})


def add_question(request):
    if request.method == "POST":
        form = AddQuestionForm(request.POST)
        if form.is_valid():
            try:
                print("Сохранение вопроса")
                question = form.save(commit=False)
                question.author = request.user
                question.save()
                return redirect("posts:detail", pk=question.id)
            except Exception as e:
                print(e)
                form.add_error(None, "Не удалось добавить вопрос")
    else:
        form = AddQuestionForm()
    return render(request, "posts/add_question.html", {"form": form})
