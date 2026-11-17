from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PostForm
from .models import Post


def create(request):
    form = PostForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
    )
    if request.method == "POST" and form.is_valid():
        post = form.save()
        messages.success(
            request,
            "Post published." if post.is_published else "Draft saved. Find it in Manage posts.",
        )
        return redirect("home")
    return render(request, "posts/create.html", {"form": form})


def post_list(request):
    posts = Post.objects.order_by("-published_at", "-pk")
    return render(request, "posts/list.html", {"posts": posts})


def edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=post,
        initial={"is_published": "true" if post.is_published else "false"},
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Changes saved.")
        return redirect("posts:list")
    return render(request, "posts/create.html", {"form": form, "editing": True})


def delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect("posts:list")
    return render(request, "posts/delete.html", {"post": post})


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk, is_published=True)
    return render(request, "posts/detail.html", {"post": post})
