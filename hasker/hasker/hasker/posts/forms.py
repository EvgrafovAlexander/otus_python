from django import forms

from .models import Question, Tag


class AddQuestionForm(forms.ModelForm):
    title = forms.CharField(max_length=255, label="Заголовок вопроса")
    text = forms.CharField(widget=forms.Textarea(attrs={"cols": 60, "rows": 10}), label="Текст вопроса")
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Question
        fields = "__all__"
        # fields = ["title", "text", "tags"]
