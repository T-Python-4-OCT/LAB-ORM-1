from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """The form used on the "add post" page — built from the Post model."""

    class Meta:
        model = Post
        fields = ["title", "content", "is_published"]
        labels = {
            "title": "عنوان المقال",
            "content": "نص المقال",
            "is_published": "انشر المقال مباشرة في الصفحة الرئيسية",
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "field__input",
                "placeholder": "مثال: كيف يغيّر الضغط العالي شكل المباراة؟",
                "maxlength": 2048,
                "data-counter": "true",
            }),
            "content": forms.Textarea(attrs={
                "class": "field__input field__textarea",
                "placeholder": "اكتب تحليلك أو رأيك أو قصتك الكروية هنا…",
                "rows": 12,
            }),
            "is_published": forms.CheckboxInput(attrs={"class": "switch__input"}),
        }
        error_messages = {
            "title": {"required": "اكتب عنواناً للمقال."},
            "content": {"required": "المقال يحتاج إلى نص."},
        }
