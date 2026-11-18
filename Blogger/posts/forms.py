from django import forms

from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ["title", "content", "category", "is_published", "image"]

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError("The title must be at least 3 characters.")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if len(content.split()) < 3:
            raise forms.ValidationError("The content must be at least 3 words.")
        return content
