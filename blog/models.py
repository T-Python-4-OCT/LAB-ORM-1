from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.




import os


class Post(models.Model):
    title = models.CharField(max_length=2048)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)

    # Image Attachment
    image = models.ImageField(
        upload_to='posts/images',
        blank=True,
        null=True
    )

    # Video Attachment
    video = models.FileField(
        upload_to='posts/videos',
        blank=True,
        null=True
    )

    # PDF Attachment
    document = models.FileField(
        upload_to='posts/files',
        blank=True,
        null=True
    )

    def clean(self):
        super().clean()

        attachments = [
            self.image,
            self.video,
            self.document
        ]

        selected = sum(bool(file) for file in attachments)

        if selected > 1:
            raise ValidationError(
                'You can upload only one attachment per post.'
            )

        allowed_types = {
            'image': ['.jpg', '.jpeg', '.png', '.webp'],
            'video': ['.mp4', '.webm'],
            'document': ['.pdf']
        }

        max_sizes = {
            'image': 5 * 1024 * 1024,
            'video': 50 * 1024 * 1024,
            'document': 10 * 1024 * 1024
        }

        for field in ['image', 'video', 'document']:
            file = getattr(self, field)

            if file:
                extension = os.path.splitext(file.name)[1].lower()

                if extension not in allowed_types[field]:
                    raise ValidationError({
                        field: 'Unsupported file type.'
                    })

                if file.size > max_sizes[field]:
                    raise ValidationError({
                        field: 'File size exceeds the allowed limit.'
                    })

    def __str__(self):
        return self.title
