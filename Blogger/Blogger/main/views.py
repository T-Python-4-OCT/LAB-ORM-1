from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Review
from django.http import HttpRequest



# Homepage
def home(request):

    posts = Post.objects.all()[0:3]

    return render(request, 'main/home.html', {
        'posts': posts
    })


# Add New Post
def add_post(request):

    if request.method == 'POST':

        title = request.POST.get('title')
        content = request.POST.get('content')
        is_published = request.POST.get('is_published')

        # Get Rating
        rating = request.POST.get('rating', '0')

        if rating not in ['0', '1', '2', '3', '4', '5']:
            rating = '0'

        # Get uploaded image
        poster = request.FILES.get('poster')

        if title and content:

            post_data = {
                'title': title,
                'content': content,
                'is_published': (is_published == 'True'),
                'rating': int(rating)
            }

            if poster:
                post_data['poster'] = poster

            Post.objects.create(**post_data)

            return redirect('home')

    return render(request, 'main/add_post.html')


# Post Details
def post_detail(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    return render(request, 'main/post_detail.html', {
        'post': post
    })


# Update Post
def update_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':

        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.is_published = request.POST.get('is_published') == 'True'

        # Update Rating
        rating = request.POST.get('rating')

        if rating in ['1', '2', '3', '4', '5']:
            post.rating = int(rating)

        # Update Poster
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


# All Posts
def all_posts(request):

    posts = Post.objects.all().order_by('-published_at')

    return render(request, 'main/all_post.html', {
        'posts': posts
    })


# Search Posts
def search_post(request):

    search = request.GET.get('search', '')
    order = request.GET.get('order', '')

    if search:

        posts = Post.objects.filter(title__icontains=search)

        if order == 'highest':
            posts = posts.order_by('-rating')

        elif order == 'lowest':
            posts = posts.order_by('rating')

        elif order == 'newest':
            posts = posts.order_by('-published_at')

        elif order == 'oldest':
            posts = posts.order_by('published_at')

    else:
        posts = []

    return render(request, 'main/search_post.html', {
        'posts': posts,
        'search': search,
        'order': order
    })


def add_review_view(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":

        new_review = Review(
            post=post,
            name=request.POST.get("name"),
            comment=request.POST.get("comment"),
            rating=request.POST.get("rating")
        )

        new_review.save()

    return redirect("post_detail", post_id=post.id)

