from django.http import HttpRequest
from django.shortcuts import redirect, render

from .models import Post


def home_view(request: HttpRequest):
    posts = Post.objects.filter(is_published=True).order_by("-published_at")
    return render(request, "main/index.html", {"posts": posts})


def add_post_view(request: HttpRequest):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        is_published = request.POST.get("is_published") == "on"

        if title and content:
            Post.objects.create(title=title, content=content, is_published=is_published)
            return redirect("main:home_view")

        return render(request, "main/add_post.html", {
            "error": "Please fill in both the title and the content.",
            "title": title,
            "content": content,
        })

    return render(request, "main/add_post.html")
