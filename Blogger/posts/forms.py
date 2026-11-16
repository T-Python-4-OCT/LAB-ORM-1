from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'is_published']
        labels = {
            'title': 'عنوان التدوينة',
            'content': 'محتوى التدوينة',
            'is_published': 'نشر التدوينة',
        }
        error_messages = {
            'title': {'required': 'عنوان التدوينة مطلوب.'},
            'content': {'required': 'محتوى التدوينة مطلوب.'},
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'أدخل عنوان التدوينة ...', 'maxlength': 2048}),
            'content': forms.Textarea(attrs={'placeholder': 'اكتب محتوى التدوينة هنا ...', 'rows': 7}),
        }
