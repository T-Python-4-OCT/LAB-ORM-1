from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

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
            post = Post(title=title, content=content, is_published=is_published)
            if "image" in request.FILES:
                post.image = request.FILES["image"]
            post.save()
            return redirect("main:post_detail_view", post_id=post.id)

        return render(request, "main/add_post.html", {
            "error": "Please fill in both the title and the content.",
            "title": title,
            "content": content,
        })

    return render(request, "main/add_post.html")


def post_detail_view(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, "main/post_detail.html", {"post": post})


def post_update_view(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if title and content:
            post.title = title
            post.content = content
            post.is_published = request.POST.get("is_published") == "on"
            if "image" in request.FILES:
                post.image = request.FILES["image"]
            post.save()
            return redirect("main:post_detail_view", post_id=post.id)

        return render(request, "main/post_update.html", {
            "post": post,
            "error": "Please fill in both the title and the content.",
        })

    return render(request, "main/post_update.html", {"post": post})


@require_POST
def post_delete_view(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect("main:home_view")
