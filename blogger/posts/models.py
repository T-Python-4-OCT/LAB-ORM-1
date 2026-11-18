from django.db import models


class Post(models.Model):
    CATEGORIES = [
        ('tech', 'Technology'),
        ('programming', 'Programming'),
        ('business', 'Business'),
        ('health', 'Health'),
        ('travel', 'Travel'),
        ('food', 'Food'),
        ('books', 'Books'),
        ('life', 'Life'),
        ('other', 'Other'),
    ]

    ICONS = {
        'tech': 'bi-cpu',
        'programming': 'bi-code-slash',
        'business': 'bi-briefcase',
        'health': 'bi-heart-pulse',
        'travel': 'bi-airplane',
        'food': 'bi-cup-hot',
        'books': 'bi-book',
        'life': 'bi-sun',
        'other': 'bi-tag',
    }

    title = models.CharField(max_length=2048)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES, default='other')
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    reading_time = models.PositiveIntegerField(default=1, editable=False)
    image = models.ImageField(upload_to='images/', default='images/default.jpg',)
    file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.reading_time = max(1, len(self.content.split()) // 200)
        if kwargs.get('update_fields') is not None:
            kwargs['update_fields'] = (*kwargs['update_fields'], 'reading_time')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def icon(self):
        return self.ICONS.get(self.category, 'bi-tag')
