
from django.db import models


class Post(models.Model):
    author = models.CharField(max_length=100, default="Anonymous")
    title = models.CharField(max_length=2048)
    content = models.TextField()
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
