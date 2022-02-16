from django.http import HttpResponse
from django.shortcuts import render

from .models import User, Question

# Create your views here.


def index(request):
    latest = Question.objects.order_by('-pub_date')[:10]
    return render(request, "index.html", {"questions": latest})
