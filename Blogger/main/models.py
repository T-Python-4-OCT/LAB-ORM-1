from django.db import models

# Create your models here.

class Category(models.TextChoices):
    NEWS = "news", "News"
    TECH = "tech", "Tech"
    SPORTS = "sports", "Sports"
    CULTURE = "culture", "Culture"
    OPINION = "opinion", "Opinion"


class Post(models.Model):

    title = models.CharField(max_length=2048)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.NEWS)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="images/", default="images/default.jpg")

    def __str__(self):
        return self.title