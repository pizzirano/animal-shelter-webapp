"""
Settings for running the tests — inherits from base.py, no dependency on .env.
"""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Dedicated SQLite for the tests (does not touch the development db)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }
}

# In-memory email — no real SMTP calls
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'test@example.test'
STAFF_EMAIL = 'staff@example.test'

# Official Google reCAPTCHA test keys — accept any token, zero network calls
RECAPTCHA_PUBLIC_KEY  = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']

# Remove debug_toolbar if present (added only by development.py)
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
MIDDLEWARE   = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]

# In-memory cache (default in base.py — confirmed)
# Rate limiting enabled by default; tests that don't exercise it use override_settings
