from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.urls import path  # noqa

from . import views

app_name = "posts"
urlpatterns = [
    # ex: /posts/
    path("", views.IndexView.as_view(), name="index"),
    # ex: /posts/5/
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /posts/register
    path("register/", views.register, name="register"),
    # ex: /posts/login
    path("login/", views.login, name="login"),
    # ex: /posts/logout
    path("logout/", LogoutView.as_view(), {"next_page": settings.LOGOUT_REDIRECT_URL}, name="logout"),
    # ex: /posts/add_question
    path("add_question/", views.add_question, name="add_question"),
]
