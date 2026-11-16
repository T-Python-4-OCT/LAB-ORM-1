"""Views of the blog: the home page with the latest posts, and the page to add a post."""

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from main.models import Post

TITLE_MAX = 2048


def home(request: HttpRequest) -> HttpResponse:
    """All the posts, newest first. Each one shows "منشور" (green) or "غير منشور" (grey) from is_published."""
    posts = Post.objects.all().order_by("-published_at")
    context = {
        "posts": posts,
        "published_count": posts.filter(is_published=True).count(),
        "unpublished_count": posts.filter(is_published=False).count(),
    }
    return render(request, "main/home.html", context)


def add_post(request: HttpRequest) -> HttpResponse:
    """GET shows the form. POST checks it, saves the post, then goes back to the home page."""
    errors = {}
    values = {"title": "", "content": "", "is_published": True}

    if request.method == "POST":
        values = {
            "title": request.POST.get("title", "").strip(),
            "content": request.POST.get("content", "").strip(),
            # An unticked checkbox is not sent at all, so a missing value means False
            "is_published": request.POST.get("is_published") == "on",
        }
        if not values["title"]:
            errors["title"] = "اكتب عنوان التدوينة."
        elif len(values["title"]) > TITLE_MAX:
            errors["title"] = f"العنوان طويل، الحد الأقصى {TITLE_MAX} حرف."
        if not values["content"]:
            errors["content"] = "اكتب محتوى التدوينة."

        if not errors:
            # published_at is not passed: auto_now_add fills it with the current date and time
            post = Post.objects.create(
                title=values["title"],
                content=values["content"],
                is_published=values["is_published"],
            )
            if post.is_published:
                messages.success(request, f"تم نشر «{post.title}».")
            else:
                messages.success(request, f"تم حفظ «{post.title}»، وتظهر في الرئيسية بشارة «غير منشور».")
            return redirect("main:home")

    context = {"errors": errors, "values": values, "title_max": TITLE_MAX}
    return render(request, "main/add_post.html", context)
