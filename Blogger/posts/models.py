from django.db import models

# Create your models here.


class Post(models.Model):

    class Category(models.TextChoices):
        NEWS = "news", "News"
        FOOTBALL = "football", "Football"
        HISTORY = "history", "History"
        CULTURE = "culture", "Culture"
        OTHER = "other", "Other"

    title = models.CharField(max_length=2048)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="posts/images/", blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)

    def __str__(self):
        return self.title

    @property
    def reading_time(self):
        words = len(self.content.split())
        return max(1, -(-words // 200))
