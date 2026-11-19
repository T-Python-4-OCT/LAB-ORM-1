
from django.db import models


class Post(models.Model):
    class Category(models.TextChoices):
        TECHNOLOGY = 'technology', 'Technology'
        EDUCATION = 'education', 'Education'
        LIFESTYLE = 'lifestyle', 'Lifestyle'
        PROGRAMMING = 'programming', 'Programming'
        OTHER = 'other', 'Other'

    title = models.CharField(max_length=2048)
    content = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER
    )

    image = models.ImageField(
        upload_to="posts/images",
        blank=True,
        null=True
    )

    poster = models.FileField(
        upload_to="posts/images",
        blank=True,
        null=True
    )
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title