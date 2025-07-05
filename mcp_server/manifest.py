from django.http import JsonResponse
from django.urls import reverse


def ai_plugin_manifest(request):
    """Return the plugin manifest used by MCP clients."""
    openapi_url = request.build_absolute_uri(reverse('openapi-schema'))
    manifest = {
        "schema_version": "v1",
        "name_for_human": "GitLab MCP",
        "name_for_model": "gitlab_mcp",
        "description_for_human": "Manage GitLab merge requests via JSON-RPC.",
        "description_for_model": (
            "Use JSON-RPC methods to list, review and manage GitLab merge requests."
        ),
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": openapi_url},
        "logo_url": "https://example.com/logo.png",
        "contact_email": "support@example.com",
        "legal_info_url": "https://example.com/legal",
    }
    return JsonResponse(manifest)
