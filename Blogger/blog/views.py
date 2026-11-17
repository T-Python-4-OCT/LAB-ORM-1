from django.shortcuts import render, redirect, get_object_or_404
from .models import Post


def home(request):
    posts = Post.objects.filter(
        is_published=True
    ).order_by('-published_at')

    return render(request, 'blog/home.html', {
        'posts': posts
    })


def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        if title and content:
            Post.objects.create(
                title=title,
                content=content,
                image=image
            )

            return redirect('home')

    return render(request, 'blog/add_post.html')


def post_detail(request, pk):
    post = get_object_or_404(
        Post,
        pk=pk,
        is_published=True
    )

    return render(request, 'blog/post_detail.html', {
        'post': post
    })


def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        if title and content:
            post.title = title
            post.content = content

            if request.FILES.get('image'):
                post.image = request.FILES.get('image')

            if request.POST.get('remove_image') == 'on':
                post.image = None

            post.save()

            return redirect('post_detail', pk=post.pk)

    return render(request, 'blog/edit_post.html', {
        'post': post
    })


def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'blog/delete_post.html', {
        'post': post
    })