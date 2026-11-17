from django.urls import path
from . import views

app_name = "posts"
urlpatterns = [
    path("posts/", views.manage_posts, name="manage"),
    path("", views.home, name="home"),
    path("posts/new/", views.create_post, name="create"),
    path("posts/<int:pk>/edit/", views.edit_post, name="edit"),
    path("posts/<int:pk>/delete/", views.delete_post, name="delete"),
]
