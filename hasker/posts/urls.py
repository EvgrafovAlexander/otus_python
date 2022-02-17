from django.urls import path

from . import views


urlpatterns = [
    # name - наименование шаблона в templates
    # /
    path("", views.index, name="index"),
    path("questions/<int:pk>/", views.question_detail, name="question_detail"),

    # профиль пользователя
    #path("<str:username>/", views.profile, name="profile")

]
