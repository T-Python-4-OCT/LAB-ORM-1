from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'is_published']
        labels = {
            'title': 'Title',
            'content': 'Content',
            'image': 'Image (optional)',
            'is_published': 'Publish immediately',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter the post title'}),
            'content': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Write your post here...'}),
            'image' : forms.ClearableFileInput(attrs={'accept' : 'image/*'}),
        }