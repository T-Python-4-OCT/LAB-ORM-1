from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib import messages

from .models import Post
from .forms import PostForm

# Create your views here.


def add_post_view(request: HttpRequest):

    post_form = PostForm()

    if request.method == "POST":
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            new_post = post_form.save()

            if new_post.is_published:
                messages.success(request, "Your post has been published.")
            else:
                messages.success(request, "Your post was saved as a draft.")

            return redirect("posts:post_detail_view", post_id=new_post.id)

    return render(request, "posts/add_post.html", {"post_form": post_form, "categories": Post.Category.choices})


def update_post_view(request: HttpRequest, post_id: int):

    post = get_object_or_404(Post, pk=post_id)
    post_form = PostForm(instance=post)

    if request.method == "POST":
        old_image = post.image.name
        post_form = PostForm(request.POST, request.FILES, instance=post)
        if post_form.is_valid():
            post = post_form.save(commit=False)

            if "image" in request.FILES or "remove_image" in request.POST:
                if old_image:
                    post.image.storage.delete(old_image)
                if "image" not in request.FILES:
                    post.image = None

            post.save()
            messages.success(request, "Your changes have been saved.")
            return redirect("posts:post_detail_view", post_id=post.id)

        post.refresh_from_db()

    return render(request, "posts/add_post.html", {"post": post, "post_form": post_form, "categories": Post.Category.choices})


def post_detail_view(request: HttpRequest, post_id: int):

    post = get_object_or_404(Post, pk=post_id)

    return render(request, "posts/post_detail.html", {"post": post})


def delete_post_view(request: HttpRequest, post_id: int):

    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        if post.image:
            post.image.delete(save=False)
        post.delete()

        messages.success(request, "The post has been deleted.")
        return redirect("main:home_view")

    return render(request, "posts/delete_post.html", {"post": post})


def search_posts_view(request: HttpRequest):

    search = request.GET.get("search", "").strip()
    category = request.GET.get("category", "")
    order_by = request.GET.get("order_by", "newest")

    posts = Post.objects.filter(is_published=True)

    if search:
        posts = posts.filter(title__icontains=search) | posts.filter(content__icontains=search)

    if category in Post.Category.values:
        posts = posts.filter(category=category)

    if order_by == "oldest":
        posts = posts.order_by("published_at")
    elif order_by == "title":
        posts = posts.order_by("title")
    else:
        posts = posts.order_by("-published_at")

    context = {
        "posts": posts,
        "search": search,
        "category": category,
        "category_label": dict(Post.Category.choices).get(category, ""),
        "order_by": order_by,
        "categories": Post.Category.choices,
    }

    return render(request, "posts/search_posts.html", context)
