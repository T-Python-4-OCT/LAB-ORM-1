from django.urls import path
from . import views


app_name = "posts"

urlpatterns = [
    path('add/', views.add_post_view, name="add_post_view"),
    path('<int:post_id>/', views.post_detail_view, name="post_detail_view"),
    path('update/<int:post_id>/', views.update_post_view, name="update_post_view"),
    path('delete/<int:post_id>/', views.delete_post_view, name="delete_post_view"),
    path('search/', views.search_posts_view, name="search_posts_view"),
]
