from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(max_length=255, label="Nickname")
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()
    email = forms.EmailField()
    avatar = forms.ImageField()

    class Meta:
        model = CustomUser
        # Для отображения всех полей: fields = "__all__"
        fields = ["username", "password1", "password2", "email", "avatar"]
