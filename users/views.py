from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

from .forms import CustomUserCreationForm, CustomUserChangeForm, ProfileForm, StudentLoginForm, StaffLoginForm
from .models import Profile

User = get_user_model()

def select_role(request):
    # After selecting role, redirect to loading page with proper login url
    if request.method == "POST":
        chosen_role = request.POST.get("role")
        if chosen_role == "student":
            redirect_url = reverse("student_login")
        elif chosen_role == "staff":
            redirect_url = reverse("staff_login")
        elif chosen_role == "admin":
            redirect_url = "/admin/"
        else:
            redirect_url = reverse("select_role")
        return render(request, "registration/loading.html", {"redirect_url": redirect_url})
    return render(request, 'landing/select_role.html')

def student_login(request):
    # Show loading before actual login page (optional on GET)
    if request.method == "GET" and request.GET.get("loading") == "1":
        return render(request, "registration/loading.html", {"redirect_url": reverse("student_login")})
    form = StudentLoginForm(request.POST or None)
    error = None
    if request.method == "POST" and form.is_valid():
        first_name = form.cleaned_data['first_name']
        admission_number = form.cleaned_data['admission_number']
        # Authenticate student using custom backend
        user = authenticate(request, first_name=first_name, admission_number=admission_number)
        if user:
            login(request, user)
            return render(request, "registration/loading.html", {"redirect_url": reverse("student_dashboard")})
        else:
            error = "Invalid first name or admission number."
    return render(request, "registration/student_login.html", {"form": form, "error": error})

def staff_login(request):
    # Show loading before actual login page (optional on GET)
    if request.method == "GET" and request.GET.get("loading") == "1":
        return render(request, "registration/loading.html", {"redirect_url": reverse("staff_login")})
    form = StaffLoginForm(request.POST or None)
    error = None
    if request.method == "POST" and form.is_valid():
        identifier = form.cleaned_data['identifier']
        user = User.objects.filter(
            Q(username__iexact=identifier) |
            Q(email__iexact=identifier) |
            Q(profile__phone__iexact=identifier)
        ).first()
        if user:
            if not user.has_usable_password():
                request.session['pw_setup_user_id'] = user.id
                return render(request, "registration/loading.html", {"redirect_url": reverse("password_setup")})
            else:
                messages.info(request, "Account found. Please login with your password.")
                return render(request, "registration/loading.html", {"redirect_url": reverse("login")})
        else:
            error = "No account found with that identifier."
    return render(request, "registration/staff_login.html", {"form": form, "error": error})

def register(request):
    if request.user.is_authenticated:
        return redirect('profile_user')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # freeze until admin approves
            user.save()
            profile = user.profile  # Get the existing profile
            profile.role = 'student'  # force student role
            profile.admission_number = profile_form.cleaned_data['admission_number']
            profile.phone = profile_form.cleaned_data.get('phone')
            profile.save()
            subject = 'Welcome to Library Management System'
            message = render_to_string('registration/welcome_email.html', {'user': user})
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            messages.info(request, "Your account was created and is pending admin approval. You will be notified when activated.")
            return render(request, "registration/loading.html", {"redirect_url": reverse("login")})
    else:
        form = CustomUserCreationForm()   
        profile_form = ProfileForm(initial={'role': 'student'})
    return render(request, 'registration/register.html', {
        'form': form,
        'profile_form': profile_form,
        'chosen_role': 'student'
    })

def custom_logout(request):
    logout(request)
    return render(request, "registration/loading.html", {"redirect_url": reverse("select_role")})

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(email=data)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Request"
                    email_template_name = "registration/password_reset_email.html"
                    context = {
                        "email": user.email,
                        "username": user.username,
                        "protocol": "http",
                        "domain": request.get_host(),
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user),
                    }
                    email = render_to_string(email_template_name, context)
                    send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email])
                return render(request, "registration/loading.html", {"redirect_url": reverse("password_reset_done")})
    else:
        password_reset_form = PasswordResetForm()
    return render(request, "registration/password_reset.html", {"form": password_reset_form})

@login_required
def profile_user(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated.')
            return render(request, "registration/loading.html", {"redirect_url": reverse("profile_user")})
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    return render(request, 'registration/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile
    })

def find_account(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        user = User.objects.filter(
            Q(username__iexact=identifier) |
            Q(email__iexact=identifier) |
            Q(profile__phone__iexact=identifier)
        ).first()
        if user:
            if not user.has_usable_password():
                request.session['pw_setup_user_id'] = user.id
                return render(request, "registration/loading.html", {"redirect_url": reverse("password_setup")})
            else:
                messages.info(request, "Account found. Please login with your password.")
                return render(request, "registration/loading.html", {"redirect_url": reverse("login")})
        else:
            messages.error(request, "No account found with that identifier.")
    return render(request, 'registration/find_account.html')

def password_setup(request):
    user_id = request.session.get('pw_setup_user_id')
    user = None
    if user_id:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            pass
    if not user:
        messages.error(request, "Session expired or invalid. Please try again.")
        return render(request, "registration/loading.html", {"redirect_url": reverse("find_account")})

    if user.has_usable_password():
        messages.info(request, "Password already set. Please login.")
        return render(request, "registration/loading.html", {"redirect_url": reverse("login")})

    password_set_success = False

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            del request.session['pw_setup_user_id']
            password_set_success = True
            # Don't redirect -- render the template with the success flag and show dashboard button
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SetPasswordForm(user)
    return render(request, 'registration/password_setup.html', {
        'form': form,
        'user': user,
        'password_set_success': password_set_success,
    })

@login_required
def student_dashboard(request):
    # Optional: Show loading before dashboard
    if request.GET.get("loading") == "1":
        return render(request, "registration/loading.html", {"redirect_url": reverse("student_dashboard")})
    return render(request, "dashboards/student/dashboard.html")

@login_required
def staff_dashboard(request):
    # Optional: Show loading before dashboard
    if request.GET.get("loading") == "1":
        return render(request, "registration/loading.html", {"redirect_url": reverse("staff_dashboard")})
    return render(request, "dashboards/staff/dashboard.html")