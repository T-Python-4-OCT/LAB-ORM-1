from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Post


HOME_POSTS_LIMIT = 3  # how many posts the homepage shows


def home(request):
    """Homepage: only the latest 3 published posts, newest first."""
    published = Post.objects.filter(is_published=True).order_by("-published_at")
    return render(request, "main/home.html", {
        "posts": published[:HOME_POSTS_LIMIT],
        "posts_count": published.count(),  # total, for the counter and the "all posts" button
    })


# sorting options for the all-posts page: ?sort=newest (default) or ?sort=oldest
SORT_OPTIONS = {
    "newest": "-published_at",  # newest first
    "oldest": "published_at",   # oldest first
}


def all_posts(request):
    """All-posts page: every published post — can be filtered by category and sorted by date."""
    posts = Post.objects.filter(is_published=True)

    category = request.GET.get("category")  # e.g. /posts/?category=tactics
    if category in Post.Category.values:
        posts = posts.filter(category=category)
    else:
        category = None

    sort = request.GET.get("sort", "newest")  # e.g. /posts/?sort=oldest
    if sort not in SORT_OPTIONS:
        sort = "newest"
    posts = posts.order_by(SORT_OPTIONS[sort])

    return render(request, "main/all_posts.html", {
        "posts": posts,
        "categories": Post.Category.choices,
        "current_category": category,
        "current_sort": sort,
    })


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
