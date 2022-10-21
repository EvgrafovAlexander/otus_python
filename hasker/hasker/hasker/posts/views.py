from django.shortcuts import render  # noqa
from django.utils import timezone
from django.views import generic

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
