from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages


from .models import Post


def home(request):
    posts = Post.objects.filter(
        is_published=True
    ).order_by('-published_at')

    return render(request, 'blog/home.html', {
        'posts': posts
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
    form_data = {
        'title': '',
        'content': '',
    }

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')

        form_data = {
            'title': title,
            'content': content,
        }

        if not title or not content:
            messages.error(request, 'Please fill in both fields.')

        elif not image:
            messages.error(request, 'Please select an image.')

        elif len(title) > 2048:
            messages.error(
                request,
                'The title must not exceed 2048 characters.'
            )

        else:
            Post.objects.create(
                title=title,
                content=content,
                image=image
            )

            messages.success(
                request,
                'Your post has been published!'
            )

            return redirect('home')

    return render(request, 'blog/add_post.html', {
        'form_data': form_data
    })



def edit_post(request, pk):
    post = get_object_or_404(
        Post,
        pk=pk,
        is_published=True
    )

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')

        if not title or not content:
            messages.error(request, 'Please fill in both fields.')

        elif len(title) > 2048:
            messages.error(
                request,
                'The title must not exceed 2048 characters.'
            )

        else:
            post.title = title
            post.content = content

            if image:
                post.image = image

            post.save()

            messages.success(
                request,
                'Your post has been updated!'
            )

            return redirect('post_detail', pk=post.pk)

    return render(request, 'blog/edit_post.html', {
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
