from django import forms
from django.apps import apps
from django.contrib.auth.forms import UserCreationForm

from .models import Answer, Question, Tag

# from hasker.users.models import CustomUser
CustomUser = apps.get_model("users", "CustomUser")


class AddQuestionForm(forms.ModelForm):
    title = forms.CharField(max_length=255, label="Заголовок вопроса")
    text = forms.CharField(widget=forms.Textarea(attrs={"cols": 60, "rows": 10}), label="Текст вопроса")
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Question
        fields = ["title", "text", "tags"]


class AddAnswerForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={"cols": 60, "rows": 10}), label="Текст ответа")

    class Meta:
        model = Answer
        fields = ["text"]


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(max_length=255, label="Никнейм")
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()
    email = forms.EmailField()
    avatar = forms.ImageField()

    class Meta:
        model = CustomUser
        # Для отображения всех полей: fields = "__all__"
        fields = ["username", "password1", "password2", "email", "avatar"]