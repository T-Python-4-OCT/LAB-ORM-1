from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import PostForm
from .models import Post


def home(request):
    posts = Post.objects.all()
    return render(request, 'blog/home.html', {'posts': posts})


def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            if post.is_published:
                messages.success(request, 'Your post was published successfully ✅')
            else:
                messages.info(request, 'Your post was saved as a draft 📝')
            return redirect('blog:home')
    else:
        form = PostForm()
    return render(request, 'blog/add_post.html', {'form': form})