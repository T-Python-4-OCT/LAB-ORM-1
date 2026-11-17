from django.urls import path

from main import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("posts/", views.all_posts, name="all_posts"),
    path("posts/new/", views.add_post, name="add_post"),
    # Path parameter: the post id is part of the link, e.g. /posts/3/update/
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("posts/<int:post_id>/update/", views.update_post, name="update_post"),
    path("posts/<int:post_id>/delete/", views.delete_post, name="delete_post"),
]
