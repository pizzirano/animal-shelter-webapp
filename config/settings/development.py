"""
Development settings
"""
from .base import *

DEBUG = True # Force debug mode in development environment (not getting from .env)
IS_LOCAL = True # Indicate local development environment (not getting from .env)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]'] # Allow local development hosts (not getting from .env)

# Database - SQLite for development environment
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Debug Toolbar
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE.insert(
    MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = [
    '127.0.0.1',
]

# Email configuration - test SMTP in development (settings can be changed in .env)
EMAIL_BACKEND = env_config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env_config('EMAIL_HOST', default='smtp-relay.brevo.com') # Using Brevo as default for development (can be changed)
EMAIL_PORT = env_config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = env_config('EMAIL_USE_TLS', default=True, cast=bool)
# Defaults let the project boot (runserver/pytest) on a fresh clone with no .env;
# set real values in .env to actually send mail from development.
EMAIL_HOST_USER = env_config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env_config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env_config('DEFAULT_FROM_EMAIL', default='noreply@example.org')
STAFF_EMAIL = env_config('STAFF_EMAIL', default='staff@example.org')
