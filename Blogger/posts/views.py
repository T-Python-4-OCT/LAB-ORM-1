from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension


def home(request):
    
    posts = Post.objects.filter(
        is_published=True
    ).order_by('-published_at')[:3]

    return render(request, 'posts/home.html', {
        'posts': posts
    })

def all_posts(request):
    posts = Post.objects.filter(is_published=True)

    search = request.GET.get('search', '').strip()
    publisher = request.GET.get('publisher', '').strip()
    starts_with = request.GET.get('starts_with', '')
    sort = request.GET.get('sort', 'newest')

    if search:
        posts = posts.filter(title__icontains=search)

    if publisher:
        posts = posts.filter(publisher_name__icontains=publisher)

    if starts_with:
        posts = posts.filter(title__istartswith=starts_with)

    if sort == 'oldest':
        posts = posts.order_by('published_at', 'id')
    elif sort == 'title':
        posts = posts.order_by('title', 'id')
    else:
        posts = posts.order_by('-published_at', '-id')

    return render(request, 'posts/all_posts.html', {
        'posts': posts,
        'search': search,
        'publisher': publisher,
        'starts_with': starts_with,
        'sort': sort,
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    return render(request, 'posts/detail.html', {
        'post': post
    })


def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        publisher_name = request.POST.get('publisher_name', '').strip()
        content = request.POST.get('content', '').strip()
        poster = request.FILES.get('poster')

        errors = []

        # Title validation
        if not title:
            errors.append("Post title is required.")
        elif len(title) < 3:
            errors.append("Title must be at least 3 characters.")
        elif len(title) > 100:
            errors.append("Title cannot exceed 100 characters.")

        # Publisher validation
        if not publisher_name:
            errors.append("Publisher name is required.")
        elif len(publisher_name) < 2:
            errors.append("Publisher name must be at least 2 characters.")
        elif len(publisher_name) > 100:
            errors.append("Publisher name cannot exceed 100 characters.")

        # Content validation
        if not content:
            errors.append("Post content is required.")
        elif len(content) < 10:
            errors.append("Content must be at least 10 characters.")

        # Image validation
        if poster:
            try:
                validate_image_file_extension(poster)
            except ValidationError:
                errors.append("Only valid image extensions are allowed.")

            if poster.size > 5 * 1024 * 1024:
                errors.append("Image size must not exceed 5 MB.")

        # Save post
        if not errors:
            Post.objects.create(
                title=title,
                publisher_name=publisher_name,
                content=content,
                poster=poster if poster else 'images/default.jpg'
            )
            return redirect('posts:home')

        return render(request, 'posts/add_post.html', {
            'errors': errors,
            'title': title,
            'publisher_name': publisher_name,
            'content': content,
        })

    return render(request, 'posts/add_post.html')

def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        publisher_name = request.POST.get('publisher_name', '').strip()
        content = request.POST.get('content', '').strip()

        if (
            title and content
            and 2 <= len(publisher_name) <= 100
            and len(title) <= 2048
        ):
            post.title = title
            post.publisher_name = publisher_name
            post.content = content

            if request.FILES.get('poster'):
                post.poster = request.FILES['poster']
            
            post.save()

            return redirect('posts:detail', post_id=post.id)

        return render(request, 'posts/update_post.html', {
            'post': post,
            'error': 'Please enter a valid title, publisher name and content.'
        })

    return render(request, 'posts/update_post.html', {'post': post})

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('posts:home')

    return render(request, 'posts/delete_post.html', {
        'post': post
    })