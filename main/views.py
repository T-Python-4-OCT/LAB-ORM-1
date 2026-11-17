from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from .models import Post


def home(request: HttpRequest):
    sort = request.GET.get("sort", "newest")
    category = request.GET.get("category", "")
    q = request.GET.get("q", "")

    posts = Post.objects.all()

    allowed = [value for value, label in Post.CATEGORY_CHOICES]
    if category in allowed:
        posts = posts.filter(category=category)
    else:
        category = ""

    if q:
        posts = posts.filter(title__icontains=q)

    if sort == "oldest":
        posts = posts.order_by("published_at")
    else:
        posts = posts.order_by("-published_at")

    category_tabs = []
    for value, label in Post.CATEGORY_CHOICES:
        count = Post.objects.filter(category=value).count()
        category_tabs.append((value, label, count))

    return render(request, "main/home.html", {
        "posts": posts,
        "sort": sort,
        "category": category,
        "q": q,
        "category_tabs": category_tabs,
        "total": Post.objects.count(),
    })


def post_detail(request: HttpRequest, post_id: int):
    post = Post.objects.get(id=post_id)
    return render(request, "main/post_detail.html", {"post": post})


def save_post(request: HttpRequest, post: Post) -> dict:
    post.title = request.POST.get("title", "").strip()
    post.content = request.POST.get("content", "")
    post.is_published = request.POST.get("status") == "published"
    post.category = request.POST.get("category", "life")
    if "image" in request.FILES:
        post.image = request.FILES["image"]

    try:
        post.full_clean()
    except ValidationError as e:
        errors = {}
        for field, messages in e.message_dict.items():
            errors[field] = messages[0]
        return errors

    post.save()
    return {}


def add_post(request: HttpRequest):
    post = Post()
    errors = {}

    if request.method == "POST":
        errors = save_post(request, post)
        if not errors:
            return redirect("main:home")

    return render(request, "main/add_post.html", {
        "post": post,
        "errors": errors,
        "categories": Post.CATEGORY_CHOICES,
    })


def update_post(request: HttpRequest, post_id: int):
    post = Post.objects.get(id=post_id)
    errors = {}

    if request.method == "POST":
        errors = save_post(request, post)
        if not errors:
            return redirect("main:post_detail", post_id=post.id)

    return render(request, "main/update_post.html", {
        "post": post,
        "errors": errors,
        "categories": Post.CATEGORY_CHOICES,
    })


def delete_post(request: HttpRequest, post_id: int):
    post = Post.objects.get(id=post_id)

    if request.method == "POST":
        post.delete()
        return redirect("main:home")

    return redirect("main:update_post", post_id=post.id)