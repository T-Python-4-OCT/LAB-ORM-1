from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from .models import Post, Category

# Create your views here.

ALLOWED_CHARS = " .,!?-':()،؟"


def has_symbols(text: str) -> bool:
    for char in text:
        if not (char.isalnum() or char in ALLOWED_CHARS):
            return True
    return False


def validate_post(post: Post) -> list:
    errors = []

    if not post.title.strip():
        errors.append("Title is required.")
    elif has_symbols(post.title):
        errors.append("Title can't contain symbols like @ # $ % & *")

    if not post.content.strip():
        errors.append("Content is required.")

    if post.category not in Category.values:
        errors.append("Please choose a valid category.")

    return errors


def home_view(request: HttpRequest):

    posts = Post.objects.all()

    search = request.GET.get("q", "").strip()
    if search and not has_symbols(search):
        posts = posts.filter(title__icontains=search)

    status = request.GET.get("status", "all")
    if status == "published":
        posts = posts.filter(is_published=True)
    elif status == "unpublished":
        posts = posts.filter(is_published=False)

    category = request.GET.get("category", "all")
    if category != "all":
        posts = posts.filter(category=category)

    sort = request.GET.get("sort", "newest")
    if sort == "oldest":
        posts = posts.order_by("published_at")
    elif sort == "title":
        posts = posts.order_by("title")
    else:
        posts = posts.order_by("-published_at")

    error = ""
    if has_symbols(search):
        error = "Search can't contain symbols like @ # $ % & *"
    elif "q" in request.GET and not search and status == "all" and category == "all" and sort == "newest":
        error = "Please enter a value to search."

    return render(request, "main/index.html", {
        "posts": posts,
        "posts_count": posts.count(),
        "search": search,
        "status": status,
        "category": category,
        "categories": Category.choices,
        "sort": sort,
        "error": error,
    })


def add_post_view(request: HttpRequest):

    if request.method == "POST":
        new_post = Post(
            title=request.POST.get("title", ""),
            content=request.POST.get("content", ""),
            category=request.POST.get("category", ""),
            is_published="is_published" in request.POST,
        )

        errors = validate_post(new_post)
        if errors:
            return render(request, "main/add_post.html", {
                "post": new_post,
                "errors": errors,
                "categories": Category.choices,
            })

        if "image" in request.FILES:
            new_post.image = request.FILES["image"]
        new_post.save()

        return redirect("main:home_view")

    return render(request, "main/add_post.html", {"categories": Category.choices})


def post_detail_view(request: HttpRequest, post_id: int):

    post = get_object_or_404(Post, pk=post_id)

    return render(request, "main/post_detail.html", {"post": post})


def update_post_view(request: HttpRequest, post_id: int):

    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        post.title = request.POST.get("title", "")
        post.content = request.POST.get("content", "")
        post.category = request.POST.get("category", "")
        post.is_published = "is_published" in request.POST

        errors = validate_post(post)
        if errors:
            return render(request, "main/update_post.html", {
                "post": post,
                "errors": errors,
                "categories": Category.choices,
            })

        if "image" in request.FILES:
            post.image = request.FILES["image"]
        post.save()

        return redirect("main:home_view")

    return render(request, "main/update_post.html", {"post": post, "categories": Category.choices})


def delete_post_view(request: HttpRequest, post_id: int):

    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        if post.image.name != "images/default.jpg":
            post.image.delete(save=False)
        post.delete()

    return redirect("main:home_view")