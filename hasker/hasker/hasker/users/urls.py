from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    # ex: /users/register
    path("register/", views.register, name="register"),
    # ex: /users/login
    path("login/", views.login_view, name="login"),
    # ex: /users/logout
    path("logout/", LogoutView.as_view(), {"next_page": settings.LOGOUT_REDIRECT_URL}, name="logout"),
]
