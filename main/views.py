from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PostForm
from .models import Post

ORDERING_OPTIONS = {
    "newest": (["-published_at", "-id"], "Newest first"),
    "oldest": (["published_at", "id"], "Oldest first"),
    "title": (["title", "id"], "Title (A-Z)"),
}


def home_view(request: HttpRequest):
    # Limiting: only the latest 3 published posts
    posts = Post.objects.filter(is_published=True).order_by("-published_at", "-id")[0:3]
    total = Post.objects.filter(is_published=True).count()
    return render(request, "main/index.html", {"posts": posts, "total": total})


def all_posts_view(request: HttpRequest):
    posts = Post.objects.filter(is_published=True)

    # Filtering by category
    category = request.GET.get("category", "")
    if category in Post.Category.values:
        posts = posts.filter(category=category)

    # Ordering
    order_by = request.GET.get("order_by", "newest")
    if order_by not in ORDERING_OPTIONS:
        order_by = "newest"
    posts = posts.order_by(*ORDERING_OPTIONS[order_by][0])

    return render(request, "main/all_posts.html", {
        "posts": posts,
        "count": posts.count(),
        "categories": Post.Category.choices,
        "selected_category": category,
        "ordering_options": [(key, label) for key, (_, label) in ORDERING_OPTIONS.items()],
        "selected_order": order_by,
    })


def search_posts_view(request: HttpRequest):
    search = request.GET.get("search", "").strip()
    order_by = request.GET.get("order_by", "newest")
    if order_by not in ORDERING_OPTIONS:
        order_by = "newest"

    posts = Post.objects.none()
    if len(search) >= 3:
        posts = Post.objects.filter(
            Q(title__icontains=search) | Q(content__icontains=search),
            is_published=True,
        ).order_by(*ORDERING_OPTIONS[order_by][0])

    return render(request, "main/search_posts.html", {
        "posts": posts,
        "count": posts.count(),
        "search": search,
        "ordering_options": [(key, label) for key, (_, label) in ORDERING_OPTIONS.items()],
        "selected_order": order_by,
    })


def add_post_view(request: HttpRequest):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            return redirect("main:post_detail_view", post_id=post.id)
    else:
        form = PostForm()

    return render(request, "main/add_post.html", {"form": form})


def post_detail_view(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, "main/post_detail.html", {"post": post})


def post_update_view(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("main:post_detail_view", post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "main/post_update.html", {"form": form, "post": post})


@require_POST
def post_delete_view(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect("main:home_view")
