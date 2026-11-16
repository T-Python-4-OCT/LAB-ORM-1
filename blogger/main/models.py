from django.db import models


class Post(models.Model):
    """One blog post."""

    title = models.CharField(max_length=2048)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    # auto_now_add: Django saves the current date and time once, when the post is created
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title
