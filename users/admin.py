from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'admission_number', 'phone')
    search_fields = ('user__username', 'admission_number', 'role', 'phone')
    list_filter = ('role',)



site_header = "Library Management System"
site_title = "Kikai Girls Library Admin"
index_title = "Welcome to Library Management System Admin" 