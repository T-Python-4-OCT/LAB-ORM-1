
from django.db import transaction
from django.db.models.signals import (
    post_delete,
    pre_save,
)
from django.dispatch import receiver

from .models import Post, PostMedia


def delete_file_after_commit(field_file):
    if not field_file:
        return

    storage = field_file.storage
    filename = field_file.name

    transaction.on_commit(
        lambda: storage.delete(filename)
    )

@receiver(pre_save, sender=Post)
def remove_old_cover(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_post = Post.objects.filter(
        pk=instance.pk
    ).first()

    if old_post is None:
        return

    old_cover = old_post.cover_image
    new_cover = instance.cover_image

    old_name = old_cover.name if old_cover else ""
    new_name = new_cover.name if new_cover else ""

    if old_name and old_name != new_name:
        delete_file_after_commit(old_cover)

@receiver(post_delete, sender=Post)
def remove_post_cover(sender, instance, **kwargs):
    delete_file_after_commit(instance.cover_image)

@receiver(post_delete, sender=PostMedia)
def remove_attachment(sender, instance, **kwargs):
    delete_file_after_commit(instance.file)