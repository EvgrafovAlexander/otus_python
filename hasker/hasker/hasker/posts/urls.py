from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.urls import path  # noqa

from . import views

app_name = "posts"
urlpatterns = [
    # ex: /posts/
    path("", views.IndexView.as_view(), name="index"),
    # ex: /posts/5/
    path("<int:pk>/", views.question_view, name="detail"),
    # ex: /posts/register
    path("register/", views.register, name="register"),
    # ex: /posts/login
    path("login/", views.login_view, name="login"),
    # ex: /posts/logout
    path("logout/", LogoutView.as_view(), {"next_page": settings.LOGOUT_REDIRECT_URL}, name="logout"),
    # ex: /posts/add_question
    path("add_question/", views.add_question, name="add_question"),
    # ex: /posts/5/add_answer
    path("<int:pk>/add_answer/", views.add_answer, name="add_answer"),
    # ex: /posts/5/change_rate/1
    path("<int:pk_question>/change_rate/<int:pk_answer>/<str:vote>", views.change_rate, name="change_rate"),
    # ex: /posts/5/change_rate/1
    path("<int:pk_question>/change_question_rate/<str:vote>", views.change_question_rate, name="change_question_rate"),
]
