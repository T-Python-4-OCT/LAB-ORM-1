from django.shortcuts import render, redirect
from .models import Post


def home_view(request):
    posts = Post.objects.all().order_by("-published_at")
    return render(request, "main/home.html", {"posts": posts})

def add_post_view(request):
    if request.method == "POST":
        post = Post(
            title=request.POST["title"],
            content=request.POST["content"],
            image=request.FILES.get("image"),
        )
        post.save()
        return redirect("main:home")

    return render(request, "main/add_post.html")

def delete_post_view(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)
        post.delete()
    return redirect("main:home")

def post_detail_view(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, "main/post_detail.html", {"post": post})

def update_post_view(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == "POST":
        post.title = request.POST["title"]
        post.content = request.POST["content"]
        if "image" in request.FILES:
            post.image = request.FILES["image"]
        post.save()
        return redirect("main:post_detail", post_id=post.id)

    return render(request, "main/update_post.html", {"post": post})