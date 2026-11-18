from django.urls import path
from . import views


app_name = "main"

urlpatterns = [
    path("", views.home_view, name="home_view"),
    path("posts/add/", views.add_post_view, name="add_post_view"),
    path("posts/<int:post_id>/", views.post_detail_view, name="post_detail_view"),
    path("posts/<int:post_id>/update/", views.update_post_view, name="update_post_view"),
    path("posts/<int:post_id>/delete/", views.delete_post_view, name="delete_post_view"),
    path("posts/<int:post_id>/comments/add/", views.add_comment_view, name="add_comment_view"),
    path("comments/<int:comment_id>/delete/", views.delete_comment_view, name="delete_comment_view"),
]
