from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.select_role, name='select_role'),
    path('student-login/', views.student_login, name='student_login'),
    path('staff-login/', views.staff_login, name='staff_login'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile_user, name='profile_user'),
    path('find_account/', views.find_account, name='find_account'),
    path('password_setup/', views.password_setup, name='password_setup'),

    # Password change (for logged in users)
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'), name='password_change_done'),

    # Password reset (for users who forgot)
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
    path('dashboards/student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('dashboards/staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
]