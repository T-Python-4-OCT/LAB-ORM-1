from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Post
from django.http import HttpRequest
from django.views.decorators.http import require_POST


def home(request):
    selected = request.GET.get('category')
    sort_order = request.GET.get('sort', 'newest')
    sort_order = {
        'asc': 'reading_asc',
        'desc': 'reading_desc',
    }.get(sort_order, sort_order)
    if sort_order not in ('reading_asc', 'reading_desc', 'newest', 'oldest'):
        sort_order = 'newest'

    published = Post.objects.filter(is_published=True)
    posts = published

    if selected:
        posts = posts.filter(category=selected)

    if sort_order == 'reading_asc':
        posts = posts.order_by('reading_time', '-published_at')
    elif sort_order == 'reading_desc':
        posts = posts.order_by('-reading_time', '-published_at')
    elif sort_order == 'oldest':
        posts = posts.order_by('published_at')
    else:
        posts = posts.order_by('-published_at')

    categories = [
        {
            'value': value,
            'label': label,
            'icon': Post.ICONS[value],
            'count': published.filter(category=value).count(),
        }
        for value, label in Post.CATEGORIES
    ]

    context = {
        'posts': posts,
        'categories': categories,
        'selected': selected,
        'selected_label': dict(Post.CATEGORIES).get(selected),
        'sort_order': sort_order,
        'total': published.count(),
    }
    return render(request, 'posts/home.html', context)


def add_post(request):
    if request.method == 'POST':
        post = Post(
            title=request.POST['title'],
            content=request.POST['content'],
            category=request.POST['category'],
            is_published='is_published' in request.POST,
        )
        if request.FILES.get('image'):
            post.image = request.FILES['image']
        post.save()
        return redirect('posts:home')

    return render(request, 'posts/add_post.html', {'categories': Post.CATEGORIES})


def toggle_theme(request):
    current = request.COOKIES.get('theme', 'light')
    theme = 'light' if current == 'dark' else 'dark'

    next_url = request.GET.get('next', '/')
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = '/'

    response = redirect(next_url)
    response.set_cookie('theme', theme, max_age=60 * 60 * 24 * 365)
    return response

def post_detail_view(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    published = Post.objects.filter(is_published=True)
    categories = [
        {
            'value': value,
            'label': label,
            'icon': Post.ICONS[value],
            'count': published.filter(category=value).count(),
        }
        for value, label in Post.CATEGORIES
    ]
    context = {
        'post': post,
        'categories': categories,
        'total': published.count(),
    }
    return render(request, 'posts/post_detail.html', context)


def post_update_view(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        post.title = request.POST['title']
        post.content = request.POST['content']
        post.category = request.POST['category']
        post.is_published = 'is_published' in request.POST
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        post.save()
        return redirect('posts:post_detail', post_id=post.id)

    return render(request, 'posts/post_update.html', {'post': post, 'categories': Post.CATEGORIES})


@require_POST
def delete_post(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect('posts:home')
