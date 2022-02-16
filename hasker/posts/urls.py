from django.urls import path

from . import views


urlpatterns = [
    # /
    path("", views.index, name="index"),
    # профиль пользователя
    #path("<str:username>/", views.profile, name="profile")

]
