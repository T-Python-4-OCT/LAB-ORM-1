from django.contrib import admin
from .models import Post, PostAttachment
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher_name', 'owner', 'is_published', 'published_at')
    list_filter = ('is_published', 'published_at')
    search_fields = ('title', 'publisher_name', 'content')
    autocomplete_fields = ('owner',)

@admin.register(PostAttachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('original_filename','post','file_type','uploaded_at')
    readonly_fields = ('post','file','original_filename','file_type','uploaded_at','is_featured')
    def has_add_permission(self, request): return False
