"""
WSGI config for yakabible project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

from yakabible import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yakabible.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root=settings.STATIC_ROOT)