from django.shortcuts import render
from posts.models import Post


def home(request):
    posts = Post.objects.filter(is_published=True).order_by("-published_at", "-pk")
    return render(request, "main/index.html", {"posts": posts})
