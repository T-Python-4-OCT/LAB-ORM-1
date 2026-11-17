 
from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["author", "title", "content", "image"]

        widgets = {
            "author": forms.TextInput(attrs={
                "placeholder": "Enter your name",
                "minlength": "3",
                "maxlength": "100",
                "required": True
            }),

            "title": forms.TextInput(attrs={
                "placeholder": "Give your story a title",
                "minlength": "5",
                "maxlength": "2048",
                "required": True
            }),

            "content": forms.Textarea(attrs={
                "placeholder": "Every great story begins with a few words...",
                "rows": "9",
                "minlength": "20",
                "required": True
            }),

            "image": forms.FileInput(attrs={
                "accept": ".jpg,.jpeg,.png,.webp",
                "class": "upload-input"
            })
        }

    def clean_author(self):
        author = self.cleaned_data["author"].strip()

        if len(author) < 3:
            raise forms.ValidationError(
                "Author name must contain at least 3 characters."
            )

        return author

    def clean_title(self):
        title = self.cleaned_data["title"].strip()

        if len(title) < 5:
            raise forms.ValidationError(
                "Post title must contain at least 5 characters."
            )

        return title

    def clean_content(self):
        content = self.cleaned_data["content"].strip()

        if len(content) < 20:
            raise forms.ValidationError(
                "Your story must contain at least 20 characters."
            )

        return content

    def clean_image(self):
        image = self.cleaned_data.get("image")

        if isinstance(image, UploadedFile):
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Image size must not exceed 5 MB."
                )

            if image.image.format not in ["JPEG", "PNG", "WEBP"]:
                raise forms.ValidationError(
                    "Only JPG, JPEG, PNG and WebP images are allowed."
                )

        return image
