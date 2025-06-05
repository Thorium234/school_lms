from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from .forms import CustomUserCreationForm
import random
import string

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import render, redirect
from .forms import CustomUserChangeForm  # We'll create this next



def generate_random_password():
    length = 12
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def register(request):
    if request.user.is_authenticated:
        return redirect('profile_user')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send welcome email
            subject = 'Welcome to Library Management System'
            message = render_to_string('registration/welcome_email.html', {
                'user': user,
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            
            # Auto-login after registration
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('profile_user')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(email=data)
            if associated_users.exists():
                for user in associated_users:
                    # Generate random temporary password
                    temp_password = generate_random_password()
                    user.set_password(temp_password)
                    user.save()
                    
                    # Send email with temporary password
                    subject = "Password Reset Request"
                    email_template_name = "registration/password_reset_email.html"
                    context = {
                        "email": user.email,
                        "username": user.username,
                        "temp_password": temp_password,
                        "protocol": "http",
                        "domain": request.get_host(),
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user),
                    }
                    email = render_to_string(email_template_name, context)
                    send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email])
                    
                return redirect("password_reset_done")
    else:
        password_reset_form = PasswordResetForm()
    return render(request, "registration/password_reset.html", {"form": password_reset_form})



@login_required
def profile_user(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_user')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'registration/profile.html', {
        'user': request.user,
        'form': form
    })