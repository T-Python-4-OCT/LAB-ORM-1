from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]  # noqa: RUF012

        widgets = { # noqa: RUF012
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Enter post title",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "placeholder": "Write your post...",
                    "rows": 8,
                }
            ),
        }