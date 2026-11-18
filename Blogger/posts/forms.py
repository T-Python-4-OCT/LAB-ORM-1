from django import forms
from .models import Comment, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["name", "content"]
        labels = {"name": "Your name", "content": "Your comment"}
        help_texts = {"content": "Up to 2,000 characters. Your name and comment will be public."}
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "content": forms.Textarea(attrs={"rows": 4}),
        }


class PostForm(forms.ModelForm):
    rating = forms.TypedChoiceField(choices=[("", "Not rated")] + [(str(n), str(n)) for n in range(1, 6)], coerce=int, empty_value=None, required=False, label="Rating (1–5)")
    is_published = forms.TypedChoiceField(
        label="Publication status",
        choices=[("true", "Published"), ("false", "Not published")],
        coerce=lambda value: value == "true",
        initial="true",
        help_text="Only published posts appear on the homepage.",
    )

    class Meta:
        model = Post
        fields = ["title", "content", "image", "rating", "is_published"]
        labels = {"title": "Post title", "content": "Post content", "image": "Cover image"}
