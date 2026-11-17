from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = [
            'title',
            'content',
            'poster',
            'is_published',
        ]

        labels = {
            'title': 'عنوان التدوينة',
            'content': 'محتوى التدوينة',
            'poster': 'صورة التدوينة',
            'is_published': 'نشر التدوينة',
        }

        error_messages = {
            'title': {
                'required': 'عنوان التدوينة مطلوب.',
                'max_length': 'عنوان التدوينة طويل جدا.',
            },
            'content': {
                'required': 'محتوى التدوينة مطلوب.',
            },
            'poster': {
                'invalid_image': 'يرجى اختيار صورة صحيحة.',
            },
        }

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'أدخل عنوان التدوينة ...',
            }),

            'content': forms.Textarea(attrs={
                'placeholder': 'اكتب محتوى التدوينة هنا ...',
                'rows': 7,
            }),

            'poster': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'image-input',
            }),
        }