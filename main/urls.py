from django.urls import path

from . import views

app_name = "main"

urlpatterns = [
    path("", views.home_view, name="home_view"),
    path("posts/", views.all_posts_view, name="all_posts_view"),
    path("posts/search/", views.search_posts_view, name="search_posts_view"),
    path("posts/add/", views.add_post_view, name="add_post_view"),
    path("posts/<int:post_id>/", views.post_detail_view, name="post_detail_view"),
    path("posts/<int:post_id>/update/", views.post_update_view, name="post_update_view"),
    path("posts/<int:post_id>/delete/", views.post_delete_view, name="post_delete_view"),
]
