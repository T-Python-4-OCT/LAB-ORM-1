from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    is_published = forms.TypedChoiceField(
        label="Publication status",
        choices=[("true", "Published"), ("false", "Not published")],
        coerce=lambda value: value == "true",
        initial="true",
    )

    class Meta:
        model = Post
        fields = ["title", "content", "is_published"]
