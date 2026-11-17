import logging
from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import PostAttachment
logger = logging.getLogger(__name__)
@receiver(post_delete, sender=PostAttachment)
def remove_stored_file(sender, instance, **kwargs):
    name, storage = instance.file.name, instance.file.storage
    def cleanup():
        try:
            if name and not PostAttachment.objects.filter(file=name).exists(): storage.delete(name)
        except OSError:
            logger.exception('Attachment storage cleanup failed')
    transaction.on_commit(cleanup)
