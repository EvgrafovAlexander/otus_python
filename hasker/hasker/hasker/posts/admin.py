# flake8: noqa: F401

from django.contrib import admin

from .models import Answer, AnswerVote, Question, QuestionVote, Tag


# Register your models here.
class PostInline(admin.TabularInline):
    model = Question.tags.through


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "text", "pub_date", "author", "tags_list")
    list_filter = ["pub_date"]
    search_fields = ["title"]
    filter_horizontal = ["tags"]

    def tags_list(self, obj):
        return "\n".join([t.name for t in obj.tags.all()])


class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ("name",)
    list_filter = ["name"]
    search_fields = ["name"]
    inlines = [
        PostInline,
    ]


class AnswerAdmin(admin.ModelAdmin):
    list_display = ("text",)
    list_filter = ["text"]
    search_fields = ["text"]


class QuestionVoteAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "is_plus")


class AnswerVoteAdmin(admin.ModelAdmin):
    list_display = ("user", "answer", "is_plus")


admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswerVote, AnswerVoteAdmin)
admin.site.register(QuestionVote, QuestionVoteAdmin)
