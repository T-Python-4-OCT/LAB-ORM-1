from django.shortcuts import render, redirect
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
        )
        new_post.save()

        if new_post.is_published:
            messages.success(request, "Your post has been published.")
        else:
            messages.success(request, "Your post was saved as a draft.")

        return redirect("main:home_view")

    return render(request, "posts/add_post.html")
