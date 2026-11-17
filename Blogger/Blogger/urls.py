
from django.contrib import admin
from django.urls import path
from BlogApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.HomeView, name="home"),
    path("add/", views.AddPostView, name="add_post"),

    path(
        'post/<int:pk>/',
        views.PostDetailView,
        name='post_detail'
    ),

    path(
        'post/<int:pk>/edit/',
        views.EditPostView,
        name='edit_post'
    ),

    path(
        'post/<int:pk>/delete/',
        views.DeletePostView,
        name='delete_post'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
