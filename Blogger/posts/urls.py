from django.urls import path
from . import views


app_name = "posts"

urlpatterns = [
    path('add/', views.add_post_view, name="add_post_view"),
]
