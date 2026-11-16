# Create your views here.
from django.shortcuts import render, redirect
from .models import Post
from django.shortcuts import render, redirect, get_object_or_404

def home(request):
    posts = Post.objects.filter(is_published=True).order_by('-published_at')

    return render(request, 'blog/home.html', {
        'posts': posts
    })


def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        Post.objects.create(
            title=title,
            content=content
        )

        return redirect('home')

    return render(request, 'blog/add_post.html')

def post_detail(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        is_published=True
    )

    return render(request, 'blog/post_detail.html', {
        'post': post
    })