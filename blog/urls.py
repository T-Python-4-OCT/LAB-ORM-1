from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/new/', views.add_post, name='add_post'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', views.update_post, name='update_post'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
]
