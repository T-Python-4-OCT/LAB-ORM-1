from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib import messages

from .models import Post

# Create your views here.


def add_post_view(request: HttpRequest):

    if request.method == "POST":
        new_post = Post(
            title=request.POST["title"],
            content=request.POST["content"],
            is_published="is_published" in request.POST,  # checkbox is only sent when checked
            image=request.FILES.get("image"),
        )
        new_post.save()

        if new_post.is_published:
            messages.success(request, "Your post has been published.")
        else:
            messages.success(request, "Your post was saved as a draft.")

        return redirect("main:home_view")

    return render(request, "posts/add_post.html")


def update_post_view(request: HttpRequest, post_id: int):

    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        post.title = request.POST["title"]
        post.content = request.POST["content"]
        post.is_published = "is_published" in request.POST

        if "image" in request.FILES:
            if post.image:
                post.image.delete(save=False)
            post.image = request.FILES["image"]
        elif "remove_image" in request.POST and post.image:
            post.image.delete(save=False)

        post.save()
        messages.success(request, "Your changes have been saved.")
        return redirect("main:home_view")

    return render(request, "posts/add_post.html", {"post": post})


def delete_post_view(request: HttpRequest, post_id: int):

    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        if post.image:
            post.image.delete(save=False)
        post.delete()

        messages.success(request, "The post has been deleted.")
        return redirect("main:home_view")

    return render(request, "posts/delete_post.html", {"post": post})
