from pathlib import Path
from uuid import uuid4

from django.db import models
from django.conf import settings
from .validators import validate_publisher_name, validate_article_title, validate_article_content
from .upload_validators import validate_upload


class Post(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="posts")
    publisher_name = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )
    title = models.CharField(max_length=2048)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.publisher_name:
            validate_publisher_name(self.publisher_name)
        if self.title:
            validate_article_title(self.title)
        if self.content:
            validate_article_content(self.content)

    def __str__(self):
        return f"{self.title} ({self.publisher_name})" if self.publisher_name else self.title

    def can_manage(self, user):
        return user.is_authenticated and (user.is_staff or user.is_superuser or self.owner_id == user.pk)

    def get_image_url(self, is_detail=False):
        images = [attachment for attachment in self.attachments.all() if attachment.file_type.startswith('image/')]
        for attachment in images:
            if attachment.is_featured and attachment.file_type.startswith('image/'):
                from django.urls import reverse
                return reverse('blog:attachment', args=[attachment.pk])
        if images:
            from django.urls import reverse
            return reverse('blog:attachment', args=[images[0].pk])
        if self.id == 1:
            return '/static/blog/img/posts/siyaq-city.webp'
        elif self.id == 2:
            return '/static/blog/img/posts/siyaq-reading.webp'
        return '/static/blog/img/posts/default-cover.svg'

def upload_path(instance, filename):
    ext = Path(filename).suffix.lower()
    folder = 'images' if ext in ['.jpg','.jpeg','.png','.webp','.gif'] else ('pdf' if ext == '.pdf' else 'documents')
    return f'{folder}/{uuid4().hex}{ext}'
class PostAttachment(models.Model):
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=upload_path, validators=[validate_upload])
    original_filename = models.CharField(max_length=200)
    file_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    class Meta:
        ordering = ['uploaded_at', 'id']
        constraints = [models.UniqueConstraint(fields=['post'], condition=models.Q(is_featured=True), name='one_featured_attachment')]
    def __str__(self): return self.original_filename
