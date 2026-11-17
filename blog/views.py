from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PostForm
from .models import Post


def home(request):
    query = request.GET.get('q', '').strip()
    published_filter = request.GET.get('published', '')
    ordering = request.GET.get('sort', 'newest')

    posts = Post.objects.all()
    if query:
        posts = posts.filter(title__contains=query)

    if published_filter == 'true':
        posts = posts.filter(is_published=True)
    elif published_filter == 'false':
        posts = posts.filter(is_published=False)

    ordering_options = {
        'newest': '-published_at',
        'oldest': 'published_at',
    }
    if ordering not in ordering_options:
        ordering = 'newest'

    posts = posts.order_by(ordering_options[ordering])
    result_count = posts.count()
    posts = posts[:5]

    return render(request, 'blog/home.html', {
        'posts': posts,
        'query': query,
        'published_filter': published_filter,
        'ordering': ordering,
        'result_count': result_count,
    })

def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            if post.is_published:
                messages.success(request, 'Your post was published successfully ✅')
            else:
                messages.info(request, 'Your post was saved as a draft 📝')
            return redirect('blog:home')
    else:
        form = PostForm()
    return render(request, 'blog/add_post.html', {'form': form})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def update_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your post was updated successfully ✅')
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})


@require_POST
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.success(request, 'Your post was deleted successfully.')
    return redirect('blog:home')


