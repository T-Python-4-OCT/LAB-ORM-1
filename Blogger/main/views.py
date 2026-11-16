from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import PostForm
from .models import Post


def home(request):
    """Homepage: the latest published posts, newest first."""
    posts = Post.objects.filter(is_published=True).order_by("-published_at")
    return render(request, "main/home.html", {"posts": posts})


def add_post(request):
    """Add-post page: shows an empty form (GET) or saves a new post (POST)."""
    if request.method == "POST":
        form = PostForm(request.POST)
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
