from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "posts"
urlpatterns = [
    # ex: /posts/
    path("", views.IndexViewLast.as_view(), name="index"),
    # ex: /posts/hot/
    path("hot/", views.IndexViewHot.as_view(), name="index_hot"),
    # ex: /posts/search/
    path("search/", views.SearchResultsList.as_view(), name="search_results"),
    # ex: /posts/search_by_tag/
    path("tag/<str:tag>", views.IndexViewByTag.as_view(), name="search_by_tag"),
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
    # ex: posts/change_answer_rate/
    path("change_answer_rate/", views.change_answer_rate, name="change_answer_rate"),
    # ex: /posts/change_question_rate/
    path("change_question_rate/", views.change_question_rate, name="change_question_rate"),
    # ex: /posts/cancel_answer_vote/
    path("cancel_answer_vote/", views.cancel_answer_vote, name="cancel_answer_vote"),
    # ex: /posts/cancel_question_vote/
    path("cancel_question_vote/", views.cancel_question_vote, name="cancel_question_vote"),
    # ex: /posts/5/choose_the_best/1
    path("<int:pk_question>/choose_the_best/<int:pk_answer>", views.choose_the_best, name="choose_the_best"),
]
