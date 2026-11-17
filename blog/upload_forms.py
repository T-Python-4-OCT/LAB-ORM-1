from django import forms
from django.conf import settings
import hashlib
from .upload_validators import validate_upload
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'accept':'.jpg,.jpeg,.png,.webp,.gif,.pdf,.docx,.txt,.xlsx,.pptx'}))
        super().__init__(*args, **kwargs)
    def clean(self, data, initial=None):
        files = data if isinstance(data, (list,tuple)) else ([data] if data else [])
        if len(files) > settings.MAX_POST_ATTACHMENTS:
            raise forms.ValidationError('يمكنك إرفاق ٥ ملفات كحد أقصى.')
        result = []
        seen = set()
        for file in files:
            file = super().clean(file, initial)
            file.validated_type = validate_upload(file)
            digest = hashlib.sha256(file.read()).digest()
            file.seek(0)
            if digest in seen:
                raise forms.ValidationError('تم اختيار نفس الملف أكثر من مرة.')
            seen.add(digest)
            result.append(file)
        return result
