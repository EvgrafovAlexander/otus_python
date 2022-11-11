from django import forms

from .models import Answer, Question


class AddQuestionForm(forms.ModelForm):
    title = forms.CharField(max_length=255, label="Title", widget=forms.TextInput)
    text = forms.CharField(widget=forms.Textarea(attrs={"cols": 60, "rows": 10}), label="Question")
    tags = forms.CharField(max_length=255, label="Tag", widget=forms.TextInput)

    class Meta:
        model = Question
        fields = ["title", "text", "tags"]


class AddAnswerForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={"cols": 60, "rows": 10}), label="Answer")

    class Meta:
        model = Answer
        fields = ["text"]
