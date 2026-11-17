
from .models import Post
from .forms import PostForm
from django.shortcuts import redirect, render, get_object_or_404


def HomeView(request):
    posts = Post.objects.filter(is_published=True).order_by('-published_at')
    return render(request, 'BlogApp/home.html', {'posts': posts})


def AddPostView(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PostForm()

    return render(request, 'BlogApp/add_post.html', {'form': form})


def PostDetailView(request, pk):
    post = get_object_or_404(Post, pk=pk, is_published=True)
    return render(request, 'BlogApp/post_detail.html', {'post': post})


# Edit Post
def EditPostView(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PostForm(instance=post)

    return render(request, 'BlogApp/edit_post.html', {
        'form': form,
        'post': post
    })


# Delete Post
def DeletePostView(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'BlogApp/delete_post.html', {
        'post': post
    })
