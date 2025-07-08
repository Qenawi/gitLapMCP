"""WSGI config for clean_mcp_init project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clean_mcp_init.settings')

application = get_wsgi_application()
