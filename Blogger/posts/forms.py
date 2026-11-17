from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    is_published = forms.TypedChoiceField(
        label="Publication status",
        choices=[("true", "Published"), ("false", "Not published")],
        coerce=lambda value: value == "true",
        initial="true",
        help_text="Only published posts appear on the homepage.",
    )

    class Meta:
        model = Post
        fields = ["title", "content", "image", "is_published"]
        labels = {"title": "Post title", "content": "Post content", "image": "Cover image"}
