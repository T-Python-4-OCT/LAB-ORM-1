from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import PostForm
from .models import Post

# Create your views here.

def home(request):
    posts = Post.objects.all()
    return render(request, 'posts/home.html', {'posts': posts})


def add_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'تم حفظ التدوينة بنجاح')
        return redirect('posts:home')
    return render(request, 'posts/add_post.html', {'form': form})

