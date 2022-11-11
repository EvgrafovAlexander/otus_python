from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import RegisterUserForm


# Create your views here.
def register(request):
    """Регистрация нового пользователя"""
    if request.method == "POST":
        form = RegisterUserForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                new_user = form.save(commit=False)
                new_user.email = form.cleaned_data["email"]
                new_user.avatar = form.cleaned_data["avatar"]
                new_user.save()
                return redirect("users:login")
            except Exception:
                form.add_error(None, "Failed to add user")
    else:
        form = RegisterUserForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    """Аутентификация пользователя"""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("posts:index")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="users/login.html", context={"login_form": form})
