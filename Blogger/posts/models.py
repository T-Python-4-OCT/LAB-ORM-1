from django.db import models

# Create your models here.


class Post(models.Model):

    title = models.CharField(max_length=2048)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def reading_time(self):
        # ~200 words per minute (a plain property, so no migration is needed)
        words = len(self.content.split())
        return max(1, -(-words // 200))
