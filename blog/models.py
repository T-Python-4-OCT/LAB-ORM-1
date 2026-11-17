from pathlib import Path
from uuid import uuid4

from django.core.validators import FileExtensionValidator
from django.db import models
from django.templatetags.static import static


class Post(models.Model):
    title = models.CharField(max_length=2048)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)

    # Optional custom post cover
    cover_image = models.ImageField(
        upload_to="post_covers/",
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "jpg", "jpeg", "png", "webp", "gif"
                ]
            )
        ],
    )

    @property
    def cover_url(self):
        if self.cover_image:
            return self.cover_image.url

        return static("image/default_cover.png")

    def __str__(self):
        return self.title

def post_media_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()

    return (
        f"posts/{instance.post_id}/"
        f"{instance.media_type}/{uuid4().hex}{extension}"
    )

class PostMedia(models.Model):

    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        DOCUMENT = "document", "Document"

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="media"
    )

    file = models.FileField(
        upload_to=post_media_upload_path
    )

    media_type = models.CharField(
        max_length=8,
        choices=MediaType.choices
    )

    original_name = models.CharField(max_length=255)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("uploaded_at", "pk")

    def __str__(self):
        return (
            f"{self.original_name} "
            f"({self.get_media_type_display()})"
        )