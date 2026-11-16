from django import forms
from django.utils.html import strip_tags
import nh3

from .models import Post


ALLOWED_TAGS = {
    "p", "br", "h1", "h2", "h3",
    "strong", "b", "em", "i", "u", "s",
    "ul", "ol", "li", "blockquote",
    "a", "code", "pre", "span"
}

ALLOWED_ATTRIBUTES = {
    "a": {"href"},
}

ALLOWED_CLASSES = {
    "p": {"ql-align-right", "ql-align-center", "ql-align-justify", "ql-direction-rtl"},
    "h1": {"ql-align-right", "ql-align-center", "ql-direction-rtl"},
    "h2": {"ql-align-right", "ql-align-center", "ql-direction-rtl"},
    "h3": {"ql-align-right", "ql-align-center", "ql-direction-rtl"},
    "span": {"ql-size-small", "ql-size-large", "ql-size-huge"},
    "strong": set(),
    "em": set(),
    "u": set(),
    "s": set(),
    "li": {"ql-direction-rtl", "ql-align-right"},
}


def sanitize_content(value):
    return nh3.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        allowed_classes=ALLOWED_CLASSES,
        url_schemes={"http", "https", "mailto"},
    )


class PostForm(forms.ModelForm):

    class Meta:
        model = Post

        fields = [
            "title",
            "content",
            "image",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Post title",
                    "dir": "auto",
                }
            ),

            "content": forms.Textarea(
                attrs={
                    "id": "post-content",
                    "rows": 12,
                    "dir": "auto",
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                }
            ),
        }

    def clean_content(self):
        content = self.cleaned_data["content"]

        cleaned = sanitize_content(content)

        if not strip_tags(cleaned).strip():
            raise forms.ValidationError(
                "Please write some content."
            )

        return cleaned