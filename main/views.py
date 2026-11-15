from django.shortcuts import render, redirect
from django.http import HttpRequest
from .models import Post


# Create your views here.

def home_view(request: HttpRequest):
    posts = Post.objects.filter(is_published=True).order_by("-published_at")
    return render(request, "main/home.html", {"posts": posts})


def add_post_view(request: HttpRequest):
    if request.method == "POST":
        Post.objects.create(
            title=request.POST["title"],
            content=request.POST["content"],
            is_published="is_published" in request.POST,
        )
        return redirect("main:home_view")

    return render(request, "main/add_post.html")
