from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Post(models.Model):
    title = models.CharField(max_length=2048)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    poster = models.ImageField(upload_to='images/', blank=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ]
    )
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name