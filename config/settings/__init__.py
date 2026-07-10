"""
Automatic settings selector based on environment
"""
from decouple import config as env_config

environment = env_config('DJANGO_ENVIRONMENT', default='development')

print(f"⚙️  Loading settings for environment: {environment}")

if environment == 'production':
    from .production import *
elif environment == 'test':
    from .test import *  # to be created (not used)
else:
    from .development import *

print(f"✅ Settings loaded successfully for environment: {environment}")
