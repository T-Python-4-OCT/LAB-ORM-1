from django.shortcuts import render, redirect, get_object_or_404
from .models import Post


def home_view(request):
    posts = Post.objects.filter(is_published=True).order_by('-published_at')
    return render(request, 'main/home.html', {'posts': posts})


def add_post_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        is_published = request.POST.get('is_published') == 'on'
        poster = request.FILES.get('poster')

        if title and content:
            post = Post(
                title=title,
                content=content,
                is_published=is_published,
            )
            if poster:
                post.poster = poster
            post.save()
            return redirect('main:home')

    return render(request, 'main/add_post.html')


def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'main/post_detail.html', {'post': post})


def update_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        poster = request.FILES.get('poster')

        if title and content:
            post.title = title
            post.content = content
            post.is_published = request.POST.get('is_published') == 'on'
            if poster:
                post.poster = poster
            post.save()
            return redirect('main:post_detail', post_id=post.id)

    return render(request, 'main/update_post.html', {'post': post})


def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
    return redirect('main:home')