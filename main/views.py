from django.http import HttpRequest
from django.shortcuts import redirect, render

from .models import Post


def home_view(request: HttpRequest):
    posts = Post.objects.filter(is_published=True).order_by("-published_at")
    return render(request, "main/home.html", {"posts": posts})


def add_post_view(request: HttpRequest):
    if request.method == "POST":
        new_post = Post(
            title=request.POST["title"],
            content=request.POST["content"],
            is_published=request.POST.get("is_published") == "on",
        )
        new_post.save()
        return redirect("main:home")

    return render(request, "main/add_post.html")