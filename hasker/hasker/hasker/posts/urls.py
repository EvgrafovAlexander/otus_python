from django.urls import path  # noqa

from . import views

app_name = "posts"
urlpatterns = [
    # ex: /posts/
    path("", views.IndexView.as_view(), name="index"),
    # ex: /posts/5/
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
]
