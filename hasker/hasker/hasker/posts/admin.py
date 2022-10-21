from django.contrib import admin

from .models import Answer, Question, Tag


# Register your models here.
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "text", "pub_date", "author")
    list_filter = ["pub_date"]
    search_fields = ["title"]


class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ["name"]
    search_fields = ["name"]


class TagAnswer(admin.ModelAdmin):
    list_display = ("text",)
    list_filter = ["text"]
    search_fields = ["text"]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Answer, TagAnswer)
