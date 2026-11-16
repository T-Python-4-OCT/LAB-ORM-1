
from django import forms
from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter article title',
                'class': 'post-title-input'
            }),

            'content': forms.Textarea(attrs={
                'placeholder': 'Write your article here...',
                'class': 'rich-text-input',
                'id': 'id_content',
                'rows': 12
            }),

            'image': forms.ClearableFileInput(attrs={
                'class': 'post-image-input'
            })
        }
