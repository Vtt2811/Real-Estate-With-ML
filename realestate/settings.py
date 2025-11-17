import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-secret-key-for-local'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'listings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'realestate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'realestate.wsgi.application'

# Email Configuration
import os
from os import getenv

# By default, use console backend. Override with environment variables for production.
EMAIL_BACKEND = getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# For SMTP backend (production or local testing with a real email server)
EMAIL_HOST = getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = getenv('EMAIL_HOST_USER')  # Your email, from env variable
EMAIL_HOST_PASSWORD = getenv('EMAIL_HOST_PASSWORD') # Your app password, from env variable
DEFAULT_FROM_EMAIL = getenv('DEFAULT_FROM_EMAIL', 'noreply@realestate.com')

# ==============================================================================
# HOW TO CONFIGURE REAL EMAIL SENDING (EXAMPLE WITH GMAIL)
# ==============================================================================
# 1. Set the following environment variables in your system:
#
#    EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
#    EMAIL_HOST_USER='your-email@gmail.com'
#    EMAIL_HOST_PASSWORD='your-generated-16-digit-app-password'
#
# 2. For Gmail, you must:
#    a. Enable 2-Factor Authentication (2FA) on your Google Account.
#    b. Generate a 16-digit "App Password" here:
#       https://myaccount.google.com/apppasswords
#    c. Use that App Password for the EMAIL_HOST_PASSWORD variable.
# ==============================================================================

# Using a lightweight sqlite db only if needed later
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
# Serve both the original `photo/` folder and a local `static/` folder for CSS
STATICFILES_DIRS = [BASE_DIR / 'photo', BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
