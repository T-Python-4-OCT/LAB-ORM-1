from django.shortcuts import render


from django.http import HttpRequest
from .models import Post


def home(request: HttpRequest):
    posts = Post.objects.all().order_by("-published_at")
    return render(request, "main/home.html", {"posts": posts})


def add_post(request: HttpRequest):
    if request.method == "POST":
        post = Post(
            title=request.POST["title"],
            content=request.POST["content"],
            is_published=request.POST["status"] == "published",
        )
        post.save()
        return redirect("main:home")

    return render(request, "main/add_post.html")
# Create your views here.
