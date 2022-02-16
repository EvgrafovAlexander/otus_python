from django.contrib import admin

# Register your models here.
from .models import Question


class PostAdmin(admin.ModelAdmin):
    # поля, отображаемые в панели администратора
    list_display = ("pk", "author", "pub_date", "text")
    # интерфейс для поиска
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "---empty---"


admin.site.register(Question, PostAdmin)
