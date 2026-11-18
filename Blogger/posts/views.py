from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm
from .models import Post, Review
from django.http import HttpRequest


def home(request):
    status = request.GET.get('status', 'all')
    search = request.GET.get('search', '').strip()
    ordering = request.GET.get('ordering', 'newest')
    limit = request.GET.get('limit', '').strip()

    posts = Post.objects.all()

    if status == 'published':
        posts = posts.filter(is_published=True)
    elif status == 'draft':
        posts = posts.filter(is_published=False)
    else:
        status = 'all'

    if search:
        posts = posts.filter(title__icontains=search)

    if ordering == 'oldest':
        posts = posts.order_by('published_at', 'id')
    else:
        ordering = 'newest'
        posts = posts.order_by('-published_at', '-id')

    matching_count = posts.count()

    try:
        limit = int(limit)
    except ValueError:
        limit = None

    if limit is not None:
        if limit < 1:
            limit = None
        else:
            limit = min(limit, 1000)
            posts = posts[:limit]

    counts = Post.objects.aggregate(
        total=Count('id'),
        published=Count('id', filter=Q(is_published=True)),
        draft=Count('id', filter=Q(is_published=False)),
    )

    return render(request, 'posts/home.html', {
        'posts': posts,
        'status': status,
        'search': search,
        'ordering': ordering,
        'limit': limit,
        'matching_count': matching_count,
        'counts': counts,
    })


def add_post(request):
    form = PostForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'تم حفظ التدوينة بنجاح')
        return redirect('posts:home')

    return render(request, 'posts/add_post.html', {
        'form': form,
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    reviews = Review.objects.filter(
        post=post
    ).order_by('-created_at', '-id')

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'reviews': reviews,
    })


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post,
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'تم تعديل التدوينة بنجاح')
        return redirect('posts:post_detail', post_id=post.id)

    return render(request, 'posts/edit_post.html', {
        'form': form,
        'post': post,
    })


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'تم حذف التدوينة بنجاح')
        return redirect('posts:home')

    return render(request, 'posts/delete_post.html', {
        'post': post,
    })


def add_review_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        comment = request.POST.get('comment', '').strip()
        rating = request.POST.get('rating', '0')

        if name and comment and len(name) <= 1024 and rating in ['1', '2', '3', '4', '5']:
            Review.objects.create(
                post=post,
                name=name,
                comment=comment,
                rating=int(rating)
            )

            messages.success(request, 'تم إضافة التعليق والتقييم بنجاح')
        else:
            messages.error(request, 'يرجى إدخال البيانات واختيار تقييم من 1 إلى 5')

    return redirect('posts:post_detail', post_id=post.id)
