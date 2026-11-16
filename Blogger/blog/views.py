from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.views.decorators.http import require_POST

from .models import Post
from .forms import PostForm


# READ - Homepage
def home(request):
    posts = Post.objects.filter(
        is_published=True
    ).order_by("-published_at", "-pk")

    return render(request, "blog/home.html", {
        "posts": posts,
    })


# READ - Post Details
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    return render(request, "blog/post_detail.html", {
        "post": post,
    })


# CREATE - Add Post
def add_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save()

            return redirect(
                "post_detail",
                pk=post.pk
            )
    else:
        form = PostForm()

    return render(request, "blog/add_post.html", {
        "form": form,
    })


# UPDATE - Edit Post
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post
        )

        if form.is_valid():
            form.save()

            return redirect(
                "post_detail",
                pk=post.pk
            )
    else:
        form = PostForm(instance=post)

    return render(request, "blog/edit_post.html", {
        "form": form,
        "post": post,
    })


# DELETE - Delete Post
@require_POST
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    post.delete()

    return redirect("home")