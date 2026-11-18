from django.shortcuts import render
from django.http import HttpRequest

from posts.models import Post

# Create your views here.


def home_view(request: HttpRequest):

    # get only the published posts, latest first
    posts = Post.objects.filter(is_published=True).order_by("-published_at")

    featured_post = posts.first()
    other_posts = posts[1:]

    context = {
        "featured_post": featured_post,
        "other_posts": other_posts,
        "posts_count": posts.count(),
        "categories": Post.Category.choices,
    }

    return render(request, "main/index.html", context)
