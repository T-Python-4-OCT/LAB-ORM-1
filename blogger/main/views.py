"""Views of the blog: home page, all posts (filter / order / limit), one post, add, update, delete."""

from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from PIL import Image, UnidentifiedImageError

from main.models import Post

TITLE_MAX = 2048
EXCERPT_WORDS = 40   # how many words of each post the home page shows
IMAGE_MAX_MB = 5
HOME_LIMIT = 5        # the home page shows only the latest 5 posts
OTHER_POSTS = 3       # "تدوينات أخرى" under a post

# The choices of the "all posts" page. Only these values are accepted from the URL.
STATUS_CHOICES = {"all": "الكل", "published": "منشور", "unpublished": "غير منشور"}
ORDER_CHOICES = {
    "newest": ("-published_at", "الأحدث أولاً"),
    "oldest": ("published_at", "الأقدم أولاً"),
    "title": ("title", "العنوان (أ - ي)"),
}
LIMIT_CHOICES = [5, 10, 20]    # and "all" = no limit
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def check_image(image) -> str:
    """Return an error message if the uploaded file is not a real image, or an empty string if it is fine."""
    if image.content_type not in IMAGE_TYPES:
        return "الصورة لازم تكون JPG أو PNG أو WEBP أو GIF."
    if image.size > IMAGE_MAX_MB * 1024 * 1024:
        return f"حجم الصورة أكبر من {IMAGE_MAX_MB} ميجا."
    try:
        Image.open(image).verify()   # Pillow opens the file: a renamed text file fails here
    except (UnidentifiedImageError, OSError):
        return "الملف هذا مو صورة صحيحة."
    finally:
        image.seek(0)
    return ""


def clean_post(request: HttpRequest) -> tuple[dict, dict]:
    """Read the form (text from request.POST, the image from request.FILES) and return (values, errors)."""
    values = {
        "title": request.POST.get("title", "").strip(),
        "content": request.POST.get("content", "").strip(),
        # An unticked checkbox is not sent at all, so a missing value means False
        "is_published": request.POST.get("is_published") == "on",
    }
    errors = {}
    if not values["title"]:
        errors["title"] = "اكتب عنوان التدوينة."
    elif len(values["title"]) > TITLE_MAX:
        errors["title"] = f"العنوان طويل، الحد الأقصى {TITLE_MAX} حرف."
    if not values["content"]:
        errors["content"] = "اكتب محتوى التدوينة."

    image = request.FILES.get("image")
    if image:
        problem = check_image(image)
        if problem:
            errors["image"] = problem
        else:
            values["image"] = image
    return values, errors


def form_context(values: dict, errors: dict, post: Post | None = None) -> dict:
    """What the add page and the update page both need (they use the same template)."""
    return {"values": values, "errors": errors, "post": post, "title_max": TITLE_MAX, "image_max_mb": IMAGE_MAX_MB}


def home(request: HttpRequest) -> HttpResponse:
    """The latest posts only. Each one shows "منشور" (green) or "غير منشور" (grey) from is_published."""
    all_posts = Post.objects.all()
    context = {
        # Ordering: newest first.  Limiting: [:HOME_LIMIT] becomes LIMIT 5 in the SQL.
        "posts": all_posts.order_by("-published_at")[:HOME_LIMIT],
        "total_count": all_posts.count(),
        "excerpt_words": EXCERPT_WORDS,
        # Filtering: only the rows where is_published is True / False
        "published_count": all_posts.filter(is_published=True).count(),
        "unpublished_count": all_posts.filter(is_published=False).count(),
    }
    return render(request, "main/home.html", context)


def all_posts(request: HttpRequest) -> HttpResponse:
    """/posts/?status=published&q=قهوة&order=oldest&limit=10

    The choices come in the URL (a GET form), so a filtered page can be shared or refreshed.
    Filtering -> filter() / Q,  Ordering -> order_by(),  Limiting -> [:limit]
    """
    # Read the choices, and fall back to the default when a value is missing or not allowed
    status = request.GET.get("status", "all")
    if status not in STATUS_CHOICES:
        status = "all"
    order = request.GET.get("order", "newest")
    if order not in ORDER_CHOICES:
        order = "newest"
    limit = request.GET.get("limit", str(LIMIT_CHOICES[1]))
    if limit != "all" and (not limit.isdigit() or int(limit) not in LIMIT_CHOICES):
        limit = str(LIMIT_CHOICES[1])
    search = request.GET.get("q", "").strip()

    # Filtering
    posts = Post.objects.all()
    if status == "published":
        posts = posts.filter(is_published=True)
    elif status == "unpublished":
        posts = posts.filter(is_published=False)
    if search:
        # Q( ) | Q( ) = OR: the word is in the title OR in the content (icontains ignores upper/lower case)
        posts = posts.filter(Q(title__icontains=search) | Q(content__icontains=search))

    # Ordering
    posts = posts.order_by(ORDER_CHOICES[order][0])

    # Limiting (count first, before slicing: a sliced QuerySet can not be filtered again)
    found_count = posts.count()
    if limit != "all":
        posts = posts[: int(limit)]

    context = {
        "posts": posts,
        "found_count": found_count,
        "shown_count": len(posts),
        "excerpt_words": EXCERPT_WORDS,
        "status": status, "order": order, "limit": limit, "search": search,
        "status_choices": STATUS_CHOICES,
        "order_choices": {key: label for key, (_, label) in ORDER_CHOICES.items()},
        "limit_choices": LIMIT_CHOICES,
        "is_filtered": status != "all" or bool(search),
    }
    return render(request, "main/all_posts.html", context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Path parameter: for /posts/3/ Django sends post_id = 3. Shows the whole post."""
    post = get_object_or_404(Post, id=post_id)
    # Filtering + ordering + limiting together: other published posts, newest first, only 3
    other_posts = (
        Post.objects.filter(is_published=True)
        .exclude(id=post.id)
        .order_by("-published_at")[:OTHER_POSTS]
    )
    return render(request, "main/post_detail.html", {"post": post, "other_posts": other_posts})


def add_post(request: HttpRequest) -> HttpResponse:
    """GET shows the form. POST checks it, saves the post (and its image), then goes back to the home page."""
    values = {"title": "", "content": "", "is_published": True}
    errors = {}

    if request.method == "POST":
        values, errors = clean_post(request)
        if not errors:
            # published_at is not passed: auto_now_add fills it with the current date and time
            post = Post.objects.create(**values)
            if post.is_published:
                messages.success(request, f"تم نشر «{post.title}».")
            else:
                messages.success(request, f"تم حفظ «{post.title}»، وتظهر في الرئيسية بشارة «غير منشور».")
            return redirect("main:home")

    return render(request, "main/add_post.html", form_context(values, errors))


def update_post(request: HttpRequest, post_id: int) -> HttpResponse:
    """Path parameter: for /posts/3/update/ Django sends post_id = 3.
    GET shows the form filled with the post. POST saves the changes in the database.
    """
    post = get_object_or_404(Post, id=post_id)
    values = {"title": post.title, "content": post.content, "is_published": post.is_published}
    errors = {}

    if request.method == "POST":
        values, errors = clean_post(request)
        if not errors:
            new_image = values.pop("image", None)
            if new_image:
                post.image.delete(save=False)       # remove the old image file from the media folder
                post.image = new_image
            elif request.POST.get("remove_image") == "on":
                post.image.delete(save=False)
            post.title = values["title"]
            post.content = values["content"]
            post.is_published = values["is_published"]
            post.save()
            messages.success(request, f"تم تعديل «{post.title}».")
            return redirect("main:post_detail", post_id=post.id)

    return render(request, "main/add_post.html", form_context(values, errors, post))


def delete_post(request: HttpRequest, post_id: int) -> HttpResponse:
    """GET asks to confirm. POST deletes the post and its image (opening a link can never delete anything)."""
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        title = post.title
        post.image.delete(save=False)
        post.delete()
        messages.success(request, f"تم حذف «{title}».")
        return redirect("main:home")
    return render(request, "main/post_delete.html", {"post": post})
