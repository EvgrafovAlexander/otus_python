from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import generic

from .forms import AddQuestionForm
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
    return None


def login(request):
    return None


def add_question(request):
    if request.method == "POST":
        form = AddQuestionForm(request.POST)
        if form.is_valid():
            try:
                print(form.cleaned_data)
                Question.objects.create(**form.cleaned_data)
                return redirect("index")
            except Exception:
                form.add_error(None, "Не удалось добавить вопрос")
    else:
        form = AddQuestionForm()
    return render(request, "posts/add_question.html", {"form": form})
