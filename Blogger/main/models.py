from django.db import models


class Post(models.Model):
    """A football article."""

    class Category(models.TextChoices):
        GENERAL = "general", "عام"
        TACTICS = "tactics", "الخطط والتكتيك"
        REFEREEING = "refereeing", "التحكيم والقوانين"
        TRAINING = "training", "التدريبات واللياقة"

    title = models.CharField(max_length=2048)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    # auto_now_add: the date & time are set automatically when the post is created
    published_at = models.DateTimeField(auto_now_add=True)
    # the post's category — used to filter posts on the all-posts page
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    # optional cover image, saved under media/posts/
    image = models.ImageField(upload_to="posts/", default="posts/default.jpg", blank=True)

    class Meta:
        ordering = ["-published_at"]  # newest first

    def __str__(self):
        return self.title
