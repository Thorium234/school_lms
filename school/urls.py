from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('library/', include('library.urls')),
    path('', include('users.urls')),  # root is role selection page
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


site_header = "Library Management System"
site_title = "Kikai Girls Library Admin"
index_title = "Welcome to Library Management System Admin"



