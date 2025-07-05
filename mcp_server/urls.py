from django.contrib import admin
from django.urls import path, include

from .openapi import openapi_schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rpc/', include('mcp_server.jsonrpc_urls')),
    path('openapi.json', openapi_schema, name='openapi-schema'),
]
