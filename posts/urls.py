
from django.urls import path
from . import views


app_name = "posts"

urlpatterns = [
    path("", views.home, name="home"),
    path("journal/", views.all_posts, name="all_posts"),
    path("add/", views.add_post, name="add_post"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("posts/<int:post_id>/edit/", views.update_post, name="update_post"),
    path("posts/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("theme/toggle/", views.toggle_theme, name="toggle_theme"),
]
