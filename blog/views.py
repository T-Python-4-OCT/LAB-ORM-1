
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Post


def home(request):
    posts = Post.objects.filter(
        is_published=True
    ).order_by('-published_at')

    return render(request, 'blog/home.html', {
        'posts': posts
    })


def add_post(request):
    form_data = {
        'title': '',
        'content': '',
    }

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        form_data = {
            'title': title,
            'content': content,
        }

        if not title or not content:
            messages.error(request, 'Please fill in both fields.')

        elif len(title) > 2048:
            messages.error(
                request,
                'The title must not exceed 2048 characters.'
            )

        else:
            Post.objects.create(
                title=title,
                content=content
            )

            messages.success(
                request,
                'Your post has been published!'
            )

            return redirect('home')

    return render(request, 'blog/add_post.html', {
        'form_data': form_data
    })
