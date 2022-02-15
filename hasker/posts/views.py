from django.http import HttpResponse
from django.shortcuts import render

from .models import Post

# Create your views here.


def index(request):
    latest = Post.objects.order_by('-created_date')[:10]
    output = []
    for item in latest:
        output.append(item.text)
    return HttpResponse('\n'.join(output))
