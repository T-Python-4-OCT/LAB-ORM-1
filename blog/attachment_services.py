from django.db import transaction
from .models import PostAttachment
from .upload_validators import safe_filename

def save_article(form, user):
    stored = []
    try:
        with transaction.atomic():
            post = form.save(commit=False)
            if not post.pk and user.is_authenticated: post.owner = user
            post.save()
            for item in form.cleaned_data.get('remove_attachments', []): item.delete()
            use_new = True  # The first newly uploaded image replaces the article cover.
            for file in form.cleaned_data.get('attachments', []):
                item = PostAttachment(post=post, original_filename=safe_filename(file.name), file_type=file.validated_type)
                # Track successful storage writes even if the subsequent DB insert fails.
                item.file.save(file.name, file, save=False)
                stored.append((item.file.storage, item.file.name))
                if use_new and item.file_type.startswith('image/'):
                    post.attachments.filter(is_featured=True).update(is_featured=False)
                    item.is_featured = True
                    use_new = False
                item.save()
        return post
    except Exception:
        for storage, name in stored:
            try: storage.delete(name)
            except OSError: pass
        raise
