from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404

from .models import Post


def home_view(request: HttpRequest):
    posts = Post.objects.filter(is_published=True).order_by("-published_at")
    return render(request, "main/home.html", {"posts": posts})


def add_post_view(request: HttpRequest):
    if request.method == "POST":
        new_post = Post(
            title=request.POST["title"],
            content=request.POST["content"],
            image=request.FILES.get("image"),
            is_published=request.POST.get("is_published") == "on",
        )
        new_post.save()
        return redirect("main:home")

    return render(request, "main/add_post.html")
def post_detail_view(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    return render(request, "main/post_detail.html", {"post": post})
def update_post_view(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        post.title = request.POST["title"]
        post.content = request.POST["content"]
        post.is_published = request.POST.get("is_published") == "on"
        if "image" in request.FILES:
            post.image = request.FILES["image"]
        post.save()
        return redirect("main:post_detail", post_id=post.id)

    return render(request, "main/update_post.html", {"post": post})
def delete_post_view(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        post.delete()

    return redirect("main:home")