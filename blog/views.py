# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from django.core.exceptions import ValidationError

def home(request):
    posts = Post.objects.filter(
        is_published=True
    ).order_by('-published_at')[:3]

    return render(request, 'blog/home.html', {
        'posts': posts
    })

def all_stories(request):
    posts = Post.objects.filter(
        is_published=True
    ).order_by('-published_at')

    return render(request, 'blog/all_stories.html', {
        'posts': posts
    })


def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        attachment_type = request.POST.get('attachment_type')
        attachment = request.FILES.get('attachment')

        post = Post(
            title=title,
            content=content
        )

        if attachment_type:
            if attachment_type not in ['image', 'video', 'document']:
                return render(request, 'blog/add_post.html', {
                    'error': 'Invalid attachment type.'
                })

            if not attachment:
                return render(request, 'blog/add_post.html', {
                    'error': 'Please choose a file.'
                })

            setattr(post, attachment_type, attachment)

        elif attachment:
            return render(request, 'blog/add_post.html', {
                'error': 'Please select an attachment type.'
            })

        try:
            post.full_clean()
            post.save()

            return redirect('home')

        except ValidationError as error:
          return render(request, 'blog/add_post.html', {
            'errors': error.messages
       })

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



def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')

        attachment_type = request.POST.get('attachment_type')
        attachment = request.FILES.get('attachment')
        remove_attachment = request.POST.get('remove_attachment')

        attachment_fields = ['image', 'video', 'document']

        old_attachment = None

        for field in attachment_fields:
            current_file = getattr(post, field)

            if current_file:
                old_attachment = current_file
                break

        if attachment and remove_attachment:
            return render(request, 'blog/edit_post.html', {
                'post': post,
                'error': 'Choose a new file or remove the current attachment, not both.'
            })

        if attachment:
            if attachment_type not in attachment_fields:
                return render(request, 'blog/edit_post.html', {
                    'post': post,
                    'error': 'Please select an attachment type.'
                })

            for field in attachment_fields:
                setattr(post, field, None)

            setattr(post, attachment_type, attachment)

        elif attachment_type:
            return render(request, 'blog/edit_post.html', {
                'post': post,
                'error': 'Please choose a file for the selected attachment type.'
            })

        elif remove_attachment:
            for field in attachment_fields:
                setattr(post, field, None)

        try:
            post.full_clean()
            post.save()

            if old_attachment and (attachment or remove_attachment):
                old_attachment.delete(save=False)

            return redirect('post_detail', post_id=post.id)

        except ValidationError as error:
            return render(request, 'blog/edit_post.html', {
                'post': post,
                'error': error
            })

    return render(request, 'blog/edit_post.html', {
        'post': post
    })



def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        if post.image:
            post.image.delete(save=False)

        post.delete()

        return redirect('home')

    return render(request, 'blog/delete_post.html', {
        'post': post
    })