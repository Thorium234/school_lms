from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth URLs
    path('accounts/', include([
        path('register/', user_views.register, name='register'),
        path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
        path('logout/', user_views.custom_logout, name='logout'),
        path('profile/', user_views.profile_user, name='profile_user'),
        
        # Password reset URLs
        path('password_reset/', user_views.password_reset_request, name='password_reset'),
        path('password_reset/done/', 
             auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
             name='password_reset_done'),
        path('reset/<uidb64>/<token>/', 
             auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
             name='password_reset_confirm'),
        path('reset/done/', 
             auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
             name='password_reset_complete'),
    ])),
    
    # Library app
    path('library/', include('library.urls')),
    
    # Root URL redirect
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login_redirect'),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# This is the main URL configuration for the Django project.