
from django import forms
from .models import Post


class PostForm(forms.ModelForm):

    title = forms.CharField(
        max_length=2048,
        error_messages={
            'required': 'Please fill in both fields.',
            'max_length': 'The title must not exceed 2048 characters.'
        }
    )

    content = forms.CharField(
        widget=forms.Textarea,
        error_messages={
            'required': 'Please fill in both fields.'
        }
    )

    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'category',
            'image',
        ]
