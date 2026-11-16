from django.shortcuts import redirect, render
from .forms import PostForm


def create(request):
    form = PostForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("home")
    return render(request, "posts/create.html", {"form": form})
