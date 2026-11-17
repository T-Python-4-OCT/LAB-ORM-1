from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_post, name='add_post'),
    path('post/<int:post_id>/', views.post_detail, name='detail'),
    path('post/<int:post_id>/update/', views.update_post, name='update'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete'),
    path('all-posts/', views.all_posts, name='all_posts'),
]