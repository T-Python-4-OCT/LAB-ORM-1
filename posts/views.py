from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import PostForm
from .models import Post


def home(request):
    posts = Post.objects.filter(is_published=True)
    return render(request, "posts/home.html", {"posts": posts})


def create_post(request):
    form = PostForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        post = form.save()
        messages.success(request, "Your post has been published." if post.is_published else "Your unpublished post has been saved.")
        return redirect("posts:home")
    return render(request, "posts/create.html", {"form": form})
