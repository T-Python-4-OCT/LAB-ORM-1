from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "category", "image", "is_published"]
        labels = {
            "image": "Cover Image",
            "is_published": "Publish now",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Give your post a title", "minlength": 3}),
            "content": forms.Textarea(attrs={"rows": 10, "placeholder": "Write your post here...", "minlength": 10}),
            "image": forms.FileInput(attrs={"accept": "image/*"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters.")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if len(content) < 10:
            raise forms.ValidationError("Content must be at least 10 characters.")
        return content
