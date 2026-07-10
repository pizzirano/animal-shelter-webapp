"""
Pytest with a real PostgreSQL (Docker container). Everything else from test.py.
"""
from .test import *
from decouple import config as env_config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env_config('DB_NAME'),
        'USER': env_config('DB_USER'),
        'PASSWORD': env_config('DB_PASSWORD'),
        'HOST': env_config('DB_HOST', default='db'),
        'PORT': env_config('DB_PORT', default='5432'),
    }
}

# Console only — the test container has no logs/ dir
LOGGING['handlers'].pop('file', None)
LOGGING['root']['handlers'] = ['console']
for logger in LOGGING.get('loggers', {}).values():
    logger['handlers'] = [h for h in logger.get('handlers', []) if h != 'file']
