from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('add/', views.add_post_view, name='add_post'),
    path('post/<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('post/<int:post_id>/update/', views.update_post_view, name='update_post'),
    path('post/<int:post_id>/delete/', views.delete_post_view, name='delete_post'),
]