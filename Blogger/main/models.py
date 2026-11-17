from django.db import models


class Post(models.Model):
    """A football article."""

    title = models.CharField(max_length=2048)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    # auto_now_add: the date & time are set automatically when the post is created
    published_at = models.DateTimeField(auto_now_add=True)
    # optional cover image, saved under media/posts/
    image = models.ImageField(upload_to="posts/", default="posts/default.jpg", blank=True)
    class Meta:
        ordering = ["-published_at"]  # newest first

    def __str__(self):
        return self.title
