
from django import forms
from .models import Post
import bleach


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

    def clean_content(self):
        content = self.cleaned_data['content']

        allowed_tags = [
            'p', 'br', 'b', 'strong', 'i', 'em', 'u',
            'h2', 'h3', 'h4', 'ul', 'ol', 'li',
            'blockquote', 'span', 'div'
        ]

        allowed_attributes = {
            'span': ['style'],
            'p': ['style'],
            'div': ['style']
        }

        return bleach.clean(
            content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
