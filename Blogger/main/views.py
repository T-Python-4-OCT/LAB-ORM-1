from django.shortcuts import render, redirect
from .models import Post


def home_view(request):
    posts = Post.objects.filter(is_published=True).order_by('-published_at')
    return render(request, 'main/home.html', {'posts': posts})


def add_post_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        is_published = request.POST.get('is_published') == 'on'

        if title and content:
            Post.objects.create(
                title=title,
                content=content,
                is_published=is_published,
            )
            return redirect('main:home')

    return render(request, 'main/add_post.html')