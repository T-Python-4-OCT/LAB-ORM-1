from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import PostForm
from .models import Post


def home(request):
    posts = Post.objects.all().order_by('-published_at')

    return render(request, 'posts/home.html', {
        'posts': posts
    })


def add_post(request):
    form = PostForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == 'POST' and form.is_valid():
        form.save()

        messages.success(
            request,
            'تم حفظ التدوينة بنجاح'
        )

        return redirect('posts:home')

    return render(request, 'posts/add_post.html', {
        'form': form
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    return render(request, 'posts/post_detail.html', {
        'post': post
    })


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )

    if request.method == 'POST' and form.is_valid():
        form.save()

        messages.success(
            request,
            'تم تعديل التدوينة بنجاح'
        )

        return redirect('posts:post_detail', post_id=post.id)

    return render(request, 'posts/edit_post.html', {
        'form': form,
        'post': post
    })


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        post.delete()

        messages.success(
            request,
            'تم حذف التدوينة بنجاح'
        )

        return redirect('posts:home')

    return render(request, 'posts/delete_post.html', {
        'post': post
    })
