from django.db.models import F, Q
from django.shortcuts import render
from posts.models import Post
from .forms import PostFilterForm, PostSearchForm


def search(request):
    form = PostSearchForm(request.GET)
    query = ""
    posts = Post.objects.none()
    if form.is_valid():
        query = form.cleaned_data["q"]
        if query:
            posts = Post.objects.filter(is_published=True).filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).order_by("-published_at", "-pk")
    return render(request, "main/search.html", {"form": form, "query": query, "posts": posts})


def home(request):
    form = PostFilterForm(request.GET)
    posts = Post.objects.filter(is_published=True)
    if form.is_valid():
        if form.cleaned_data["rating"]:
            posts = posts.filter(rating__gte=int(form.cleaned_data["rating"]))
        order = form.cleaned_data["order"]
        if order == "oldest":
            posts = posts.order_by("published_at", "pk")
        elif order == "rating":
            posts = posts.order_by(F("rating").desc(nulls_last=True), "-published_at", "-pk")
        else:
            posts = posts.order_by("-published_at", "-pk")
        if form.cleaned_data["limit"]:
            posts = posts[:int(form.cleaned_data["limit"])]
    else:
        posts = posts.order_by("-published_at", "-pk")
    return render(request, "main/index.html", {"posts": posts, "filter_form": form})
