from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .forms import PostForm
from .models import Post


def home(request):
    posts = Post.objects.filter(is_published=True)
    return render(request, "posts/home.html", {"posts": posts})


def manage_posts(request):
    return render(request, "posts/home.html", {"posts": Post.objects.all(), "managing": True})


def create_post(request):
    form = PostForm(request.POST if request.method == "POST" else None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save()
        messages.success(request, "Your post has been published." if post.is_published else "Your unpublished post has been saved.")
        return redirect("posts:home")
    return render(request, "posts/create.html", {"form": form})


@require_http_methods(["GET", "POST"])
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(request.POST if request.method == "POST" else None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your post has been updated.")
        return redirect("posts:home")
    return render(request, "posts/create.html", {"form": form, "post": post})


@require_http_methods(["GET", "POST"])
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Your post has been deleted.")
        return redirect("posts:home")
    return render(request, "posts/delete.html", {"post": post})
