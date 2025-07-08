"""ASGI entry-point for clean_mcp_init."""

import os
import django

import clean_mcp_init.mcp_tools
from django.core.asgi import get_asgi_application
from django_mcp import mount_mcp_server

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clean_mcp_init.settings")
django.setup()

django_http_app = get_asgi_application()

application = mount_mcp_server(
    django_http_app=django_http_app,
    mcp_base_path="/mcp",
)
