import django.db.models.deletion
from django.db import migrations, models

import blog.models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostMedia",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID"
                    )
                ),
                (
                    "file",
                    models.FileField(
                        upload_to=blog.models.post_media_upload_path
                    )
                ),
                (
                    "media_type",
                    models.CharField(
                        choices=[
                            ("image", "Image"),
                            ("video", "Video"),
                            ("document", "Document")
                        ],
                        max_length=8
                    )
                ),
                (
                    "original_name",
                    models.CharField(max_length=255)
                ),
                (
                    "uploaded_at",
                    models.DateTimeField(auto_now_add=True)
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="media",
                        to="blog.post"
                    )
                ),
            ],
            options={
                "ordering": ("uploaded_at", "pk"),
            },
        ),
    ]
