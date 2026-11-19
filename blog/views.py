from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .forms import PostForm
from .models import Post


def home(request):
    search_query = request.GET.get('search', '').strip()

    posts = Post.objects.filter(is_published=True)

    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    posts = posts.order_by('-published_at')
    result_count = posts.count()
    posts = posts[:5]

    return render(request, 'blog/home.html', {
        'posts': posts,
        'search_query': search_query,
        'result_count': result_count
    })



def post_detail(request, pk):
    post = get_object_or_404(
        Post,
        pk=pk,
        is_published=True
    )

    return render(request, 'blog/post_detail.html', {
        'post': post
    })


def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Your post has been published!'
            )

            return redirect('home')

    else:
        form = PostForm()

    return render(request, 'blog/add_post.html', {
        'form': form
    })



def edit_post(request, pk):
    post = get_object_or_404(
        Post,
        pk=pk,
        is_published=True
    )

    if request.method == 'POST':
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Your post has been updated!'
            )

            return redirect('post_detail', pk=post.pk)

    else:
        form = PostForm(instance=post)

    return render(request, 'blog/edit_post.html', {
        'form': form,
        'post': post
    })



def delete_post(request, pk):
    post = get_object_or_404(
        Post,
        pk=pk,
        is_published=True
    )

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Your post has been deleted!')
        return redirect('home')

    return render(request, 'blog/delete_post.html', {
        'post': post
    })