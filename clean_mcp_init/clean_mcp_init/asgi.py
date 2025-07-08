"""
ASGI entry-point for clean_mcp_init.
Serves normal Django views + an MCP endpoint at /mcp
"""

import os, django
import clean_mcp_init.mcp_tools
from django.core.asgi import get_asgi_application
from django_mcp import mount_mcp_server        # ← import the helper  :contentReference[oaicite:1]{index=1}

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clean_mcp_init.settings")
django.setup()

# Plain Django app (admin, REST routes, …)
django_http_app = get_asgi_application()

# Wrap it with the MCP router
application = mount_mcp_server(
    django_http_app=django_http_app,
    mcp_base_path="/mcp",        # exact URL you’ll POST to (no trailing slash)
)
