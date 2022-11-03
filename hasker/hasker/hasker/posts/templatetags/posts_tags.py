from django import template
from django.apps import apps

Question = apps.get_model("posts", "Question")
register = template.Library()


@register.simple_tag()
def get_most_rate_questions():
    return Question.objects.all().order_by("-votes")[:20]
