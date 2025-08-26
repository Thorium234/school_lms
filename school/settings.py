"""
Django settings for school project.
"""

from pathlib import Path

# ===== Base Directory =====
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ===== Core Settings =====
SECRET_KEY = 'django-insecure-=!0y1pqt=(+j607gz$w&&k8h^pvpfl7(t_l+*-suof727=*ljv'
DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*', 'thoriumPaul.pythonanywhere.com']

# ===== Installed Apps =====
INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'users',
    'library',
    'widget_tweaks',
]

# ===== Middleware =====
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===== URL Configuration =====
ROOT_URLCONF = 'school.urls'

# ===== Templates =====
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'school' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'school.wsgi.application'

# ===== Database (SQLite only) =====
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ===== Password Validators =====
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===== Internationalization =====
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===== Static Files =====
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]  # if applicable
STATIC_ROOT = BASE_DIR / "staticfiles"

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'school' / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===== Media Files =====
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/thoriumPaul/media'

# ===== Email Configuration =====
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'thoriumpaul@gmail.com'
EMAIL_HOST_PASSWORD = 'bkofwiukmdksbfdi'

# ===== Authentication Backends =====
AUTHENTICATION_BACKENDS = [
    'users.backends.StaffAuthBackend',
    'users.backends.StudentAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
    'users.backends.EmailBackend',
]

# ===== Login URLs =====
LOGIN_REDIRECT_URL = 'profile_user'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'select_role'

# ===== Crispy Forms =====
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ===== Security (Production) =====
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
