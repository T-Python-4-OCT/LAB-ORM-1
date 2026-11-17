from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from blog.views import legacy_redirect
urlpatterns = [
    path('', RedirectView.as_view(url='/home/', permanent=False)),
    path('', include('blog.urls', namespace='blog')),
    path('admin/', admin.site.urls),
    path('ar/<path:subpath>', legacy_redirect),
    path('en/<path:subpath>', legacy_redirect),
    path('ar/', legacy_redirect), path('en/', legacy_redirect),
    path('ar', legacy_redirect), path('en', legacy_redirect),
]
# Media is deliberately served through the validated attachment view, even in
# development, so draft files and document response headers remain protected.
