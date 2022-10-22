from django.contrib import admin

from .models import Answer, Question, Tag


# Register your models here.
class PostInline(admin.TabularInline):
    model = Question.tags.through


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "text", "pub_date", "author", "tags_list")
    list_filter = ["pub_date"]
    search_fields = ["title"]

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


class TagAnswer(admin.ModelAdmin):
    list_display = ("text",)
    list_filter = ["text"]
    search_fields = ["text"]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Answer, TagAnswer)
