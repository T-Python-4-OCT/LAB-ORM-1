from django.db import models
from django.core.validators import MinLengthValidator


class Post(models.Model):
    CATEGORY_CHOICES = [
        ("travel", "Travel"),
        ("tech", "Tech"),
        ("food", "Food"),
        ("life", "Life"),
    ]

    title = models.CharField(
        max_length=2048,
        validators=[MinLengthValidator(5, message="Title must be at least 5 characters.")],
    )
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="images/", default="images/default.jpg")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="life")

    def __str__(self):
        return self.title