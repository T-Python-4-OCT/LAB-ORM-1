
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from .models import Post


def home(request):
    posts = Post.objects.filter(
        is_published=True
    ).order_by('-published_at')

    return render(request, 'main/home.html', {
        'posts': posts
    })


def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        poster = request.FILES.get('poster')

        if title and content and len(title) <= 2048:
            post = Post(
                title=title,
                content=content
            )

            if poster:
                post.poster = poster

            post.save()
            return redirect('home')

    return render(request, 'main/add_post.html')


def post_detail(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, id=post_id)

    return render(request, 'main/post_detail.html', {
        'post': post
    })


def edit_post(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        poster = request.FILES.get('poster')

        if title and content and len(title) <= 2048:
            post.title = title
            post.content = content

            if poster:
                post.poster = poster

            post.save()
            return redirect('post_detail', post_id=post.id)

    return render(request, 'main/edit_post.html', {
        'post': post
    })


def delete_post(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'main/delete_post.html', {
        'post': post
    })
