from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "is_published", "published_at"]
    list_filter = ["category", "is_published", "published_at"]
    search_fields = ["title", "content"]
    readonly_fields = ["published_at"]
