from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.add_post, name='add_post'),
    path('theme/', views.toggle_theme, name='toggle_theme'),
    path('post/<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('post/update/<int:post_id>/', views.post_update_view, name='post_update'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
]