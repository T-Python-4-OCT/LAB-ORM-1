from django.urls import path

from . import views

app_name = "main"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("posts/add/", views.add_post_view, name="add_post"),
    path("posts/<int:post_id>/", views.post_detail_view, name="post_detail"),
    path("posts/<int:post_id>/update/", views.update_post_view, name="update_post"),
     path("posts/<int:post_id>/delete/", views.delete_post_view, name="delete_post"),
]