from django.contrib import admin

# Register your models here.
from .models import Post


class PostAdmin(admin.ModelAdmin):
    # поля, отображаемые в панели администратора
    list_display = ("pk", "author", "created_date", "text")
    # интерфейс для поиска
    search_fields = ("text",)
    list_filter = ("created_date",)
    empty_value_display = "---empty---"


admin.site.register(Post, PostAdmin)
