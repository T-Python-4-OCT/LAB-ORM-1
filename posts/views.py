from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .forms import PostForm
from .models import Post


def home(request):
    return post_list(request, Post.objects.filter(is_published=True))


def manage_posts(request):
    return post_list(request, Post.objects.all(), managing=True)


def post_list(request, posts, managing=False):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    sort = request.GET.get("sort", "newest")
    status = request.GET.get("status", "") if managing else ""
    if query:
        # Search category names as well as the text, in Arabic and English.
        category_names = {
            Post.Category.GENERAL: ("عام", "general"),
            Post.Category.SPORTS: ("رياضة", "sports", "sport"),
            Post.Category.TECHNOLOGY: ("تقنية", "تكنولوجيا", "technology", "tech"),
            Post.Category.DAILY: ("يوميات", "daily life", "daily"),
        }
        normalized = query.casefold().replace("ة", "ه")
        if normalized.startswith("ال"):
            normalized = normalized[2:]
        matching_categories = [
            value for value, names in category_names.items()
            if any(normalized in name.casefold().replace("ة", "ه") for name in names)
        ]
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
            | Q(category__in=matching_categories)
        )
    if category in Post.Category.values:
        posts = posts.filter(category=category)
    else:
        category = ""
    if status in ("published", "draft"):
        posts = posts.filter(is_published=status == "published")
    else:
        status = ""
    if sort == "oldest":
        posts = posts.order_by("published_at", "pk")
    else:
        sort = "newest"
        posts = posts.order_by("-published_at", "-pk")
    # Paginator uses QuerySet.count() and slicing to fetch six posts per page.
    paginator = Paginator(posts, 6)
    page = paginator.get_page(request.GET.get("page"))
    filters = request.GET.copy()
    filters.pop("page", None)
    return render(request, "posts/home.html", {
        "posts": page.object_list, "page_obj": page, "result_count": paginator.count,
        "categories": Post.Category.choices, "query": query, "category": category,
        "sort": sort, "status": status, "managing": managing,
        "filter_query": filters.urlencode(),
    })


def create_post(request):
    form = PostForm(request.POST if request.method == "POST" else None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save()
        messages.success(request, "Your post has been published." if post.is_published else "Your unpublished post has been saved.")
        return redirect("posts:home")
    return render(request, "posts/create.html", {"form": form})


@require_http_methods(["GET", "POST"])
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(request.POST if request.method == "POST" else None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your post has been updated.")
        return redirect("posts:home")
    return render(request, "posts/create.html", {"form": form, "post": post})


@require_http_methods(["GET", "POST"])
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Your post has been deleted.")
        return redirect("posts:home")
    return render(request, "posts/delete.html", {"post": post})
