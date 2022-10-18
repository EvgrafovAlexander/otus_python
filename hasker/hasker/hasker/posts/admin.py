from django.contrib import admin  # noqa

from .models import Question, Tag


# Register your models here.
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "text", "pub_date", "author")
    list_filter = ["pub_date"]
    search_fields = ["title"]


class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ["name"]
    search_fields = ["name"]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
