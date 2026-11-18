from django.db import models


class Post(models.Model):
    class Category(models.TextChoices):
        GENERAL = "general", "عام"
        SPORTS = "sports", "رياضة"
        TECHNOLOGY = "technology", "تقنية"
        DAILY = "daily", "يوميات"

    title = models.CharField(max_length=2048)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to="posts/%Y/%m/", blank=True)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at", "-pk"]

    def __str__(self):
        return self.title
