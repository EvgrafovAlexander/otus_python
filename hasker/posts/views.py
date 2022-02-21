from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404

from .models import User, Question

# Create your views here.


def index(request):
    latest = Question.objects.order_by('-pub_date')[:10]
    return render(request, "index.html", {"questions": latest})


def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    return render(request, "question_detail.html", {"question": question})


class PostsLoginView(LoginView):
    template_name = "login.html"
