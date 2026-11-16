from django.shortcuts import render, redirect
from .models import Post


# Homepage
def home(request):

    posts = Post.objects.all().order_by('-published_at')

    return render(request, 'main/home.html', {
        'posts': posts
    })


# Add New Post
def add_post(request):

    if request.method == 'POST' and 'post' in request.POST:

        title = request.POST.get('title')
        content = request.POST.get('content')
        is_published = request.POST.get('is_published')

        if title and content:

            Post.objects.create(
                title=title,
                content=content,
                is_published=(is_published == 'True')
            )

            return redirect('home')

    return render(request, 'main/add_post.html')