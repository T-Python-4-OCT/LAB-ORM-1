from django.conf import settings
from django.db import models


class Post(models.Model):
    PUBLICATION_CHOICES = [
        (True, 'Published'),
        (False, 'Draft'),
    ]
    title = models.CharField(max_length=2048)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    is_published = models.BooleanField(choices=PUBLICATION_CHOICES, default=True)
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        """Return the uploaded image URL, or the default image from media."""
        if self.image:
            return self.image.url
        return f'{settings.MEDIA_URL}image/default.jpg'
