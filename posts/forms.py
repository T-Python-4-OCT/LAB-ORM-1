from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "image", "is_published"]
        labels = {"is_published": "Publish this post now"}
        widgets = {
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "title": forms.TextInput(attrs={"placeholder": "Give your story a title"}),
            "content": forms.Textarea(attrs={"placeholder": "What would you like to share?", "rows": 12}),
        }
