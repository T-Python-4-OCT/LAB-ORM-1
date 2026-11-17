
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q

from .models import Post
from .forms import PostForm


def home(request):
    posts = Post.objects.filter(
        is_published=True
    ).order_by("-published_at", "-id")[:2]

    return render(request, "posts/home.html", {"posts": posts})


def all_posts(request):
    search = request.GET.get("search", "").strip()
    ordering = request.GET.get("ordering", "newest")
    limit = request.GET.get("limit", "all")

    posts = Post.objects.filter(is_published=True)

    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(content__icontains=search)
        )

    ordering_options = {
        "newest": ("-published_at", "-id"),
        "oldest": ("published_at", "id"),
        "title_asc": ("title", "id"),
        "title_desc": ("-title", "id"),
    }

    if ordering not in ordering_options:
        ordering = "newest"

    posts = posts.order_by(*ordering_options[ordering])

    total_posts = posts.count()

    if limit in ["2", "4", "6", "12"]:
        posts = posts[:int(limit)]
    else:
        limit = "all"

    context = {
        "posts": posts,
        "search": search,
        "ordering": ordering,
        "limit": limit,
        "total_posts": total_posts,
        "displayed_posts": len(posts),
    }

    return render(request, "posts/all_posts.html", context)


def add_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save()
            return redirect("posts:post_detail", post_id=post.id)
    else:
        form = PostForm()

    return render(request, "posts/add_post.html", {"form": form})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_published=True)

    return render(request, "posts/post_detail.html", {"post": post})


def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_published=True)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            form.save()
            return redirect("posts:post_detail", post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(
        request,
        "posts/update_post.html",
        {"form": form, "post": post}
    )


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_published=True)

    if request.method == "POST":
        post.delete()
        return redirect("posts:home")

    return render(request, "posts/delete_post.html", {"post": post})


@require_POST
def toggle_theme(request):
    current_theme = request.COOKIES.get("theme", "light")
    new_theme = "light" if current_theme == "dark" else "dark"

    next_url = request.POST.get("next", "/")

    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):
        next_url = "/"

    response = redirect(next_url)

    response.set_cookie(
        "theme",
        new_theme,
        max_age=60 * 60 * 24 * 365,
        httponly=True,
        secure=request.is_secure(),
        samesite="Lax"
    )

    return response
