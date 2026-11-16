from django.shortcuts import render, redirect, get_object_or_404
from .models import Post


# Homepage
def home(request):

    posts = Post.objects.all().order_by('-published_at')

    return render(request, 'main/home.html', {
        'posts': posts
    })



# Add New Post
def add_post(request):

    if request.method == 'POST':

        title = request.POST.get('title')
        content = request.POST.get('content')
        is_published = request.POST.get('is_published')

        # Get uploaded image
        poster = request.FILES.get('poster')

        if title and content:

            post_data = {
                'title': title,
                'content': content,
                'is_published': (is_published == 'True')
            }

            if poster:
                post_data['poster'] = poster

            Post.objects.create(**post_data)

            return redirect('home')

    return render(request, 'main/add_post.html')


def post_detail(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    return render(request, 'main/post_detail.html', {
        'post': post
    })


def update_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':

        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.is_published = request.POST.get('is_published') == 'True'

        poster = request.FILES.get('poster')

        if poster:
            post.poster = poster

        post.save()

        return redirect('post_detail', post_id=post.id)

    return render(request, 'main/update_post.html', {
        'post': post
    })

# Delete Post
def delete_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':

        post.delete()

        return redirect('home')

    return redirect('post_detail', post_id=post.id)