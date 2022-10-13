from django.http import HttpResponse
from django.shortcuts import render  # noqa


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
