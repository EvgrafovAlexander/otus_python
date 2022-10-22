from django import forms

from .models import Tag


class AddQuestionForm(forms.Form):
    title = forms.CharField(max_length=255, label="Заголовок вопроса")
    text = forms.CharField(widget=forms.Textarea(attrs={"cols": 60, "rows": 10}), label="Текст вопроса")
    tags = forms.ModelChoiceField(queryset=Tag.objects.all(), label="Теги", required=False, empty_label="Тег не выбран")
