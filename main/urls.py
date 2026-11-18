from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("posts/add/", views.add_post, name="add_post"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("posts/<int:post_id>/update/", views.update_post, name="update_post"),
    path("posts/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("posts/<int:post_id>/comments/add/", views.add_comment, name="add_comment"),

]