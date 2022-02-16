from django.http import HttpResponse
from django.shortcuts import render

from .models import Post

# Create your views here.


def index(request):
    latest = Post.objects.order_by('-created_date')[:10]
    return render(request, "index.html", {"posts": latest})
