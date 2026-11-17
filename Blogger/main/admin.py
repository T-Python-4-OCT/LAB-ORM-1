from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "published_at", "image")
    list_filter = ("is_published", "category")
    search_fields = ("title", "content")
