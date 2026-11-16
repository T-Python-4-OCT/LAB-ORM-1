from django.shortcuts import render, redirect
from django.http import HttpRequest
from .models import Post


def home(request: HttpRequest):
    posts = Post.objects.all().order_by("-published_at")
    return render(request, "main/home.html", {"posts": posts})


def post_detail(request: HttpRequest, post_id: int):
    post = Post.objects.get(id=post_id)
    return render(request, "main/post_detail.html", {"post": post})


def add_post(request: HttpRequest):
    if request.method == "POST":
        post = Post(
            title=request.POST["title"],
            content=request.POST["content"],
            is_published=request.POST["status"] == "published",
        )
        if "image" in request.FILES:
            post.image = request.FILES["image"]
        post.save()
        return redirect("main:home")

    return render(request, "main/add_post.html")


def update_post(request: HttpRequest, post_id: int):
    post = Post.objects.get(id=post_id)

    if request.method == "POST":
        post.title = request.POST["title"]
        post.content = request.POST["content"]
        post.is_published = request.POST["status"] == "published"
        if "image" in request.FILES:
            post.image = request.FILES["image"]
        post.save()
        return redirect("main:post_detail", post_id=post.id)

    return render(request, "main/update_post.html", {"post": post})


def delete_post(request: HttpRequest, post_id: int):
    post = Post.objects.get(id=post_id)

    if request.method == "POST":
        post.delete()
        return redirect("main:home")

    return redirect("main:update_post", post_id=post.id)