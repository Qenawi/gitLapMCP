from django.contrib import admin
from django.urls import path, include

from .openapi import openapi_schema
from .manifest import ai_plugin_manifest

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rpc/', include('mcp_server.jsonrpc_urls')),
    path('openapi.json', openapi_schema, name='openapi-schema'),
    path('.well-known/ai-plugin.json', ai_plugin_manifest, name='ai-plugin-json'),
]
