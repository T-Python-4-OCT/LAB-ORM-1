from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Post


def home(request):
    """Homepage: the latest published posts, newest first."""
    posts = Post.objects.filter(is_published=True).order_by("-published_at")
    return render(request, "main/home.html", {"posts": posts})


def add_post(request):
    """Add-post page: shows an empty form (GET) or saves a new post (POST)."""
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)  # request.FILES carries the uploaded image
        if form.is_valid():
            post = form.save()
            if post.is_published:
                messages.success(request, f"تم نشر مقال «{post.title}» بنجاح.")
            else:
                messages.info(request, f"تم حفظ «{post.title}» كمسودة ولن يظهر في الرئيسية.")
            return redirect("main:home")
    else:
        form = PostForm()
    return render(request, "main/add_post.html", {"form": form})


def post_detail(request, post_id):
    """Detail page: one post shown in full, with edit & delete buttons."""
    post = get_object_or_404(Post, pk=post_id)
    return render(request, "main/post_detail.html", {"post": post})


def update_post(request, post_id):
    """Update page: the same form, pre-filled with the post (instance=post)."""
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()  # no new image chosen -> the current image is kept
            messages.success(request, f"تم حفظ التعديلات على «{post.title}».")
            return redirect("main:post_detail", post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, "main/update_post.html", {"form": form, "post": post})


def delete_post(request, post_id):
    """Delete page: GET asks for confirmation, POST deletes the post."""
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        title = post.title
        post.delete()
        messages.success(request, f"تم حذف مقال «{title}».")
        return redirect("main:home")
    return render(request, "main/delete_post.html", {"post": post})
