#!/usr/bin/env python
import os
import sys
from django.utils import encoding
from django.http import HttpResponse
from django.template import loader
import django.shortcuts as shortcuts

if not hasattr(encoding, "smart_text"):
    encoding.smart_text = encoding.smart_str

if not hasattr(shortcuts, "render_to_response"):
    def render_to_response(
        template_name,
        context=None,
        content_type=None,
        status=None,
        using=None,
    ):
        content = loader.render_to_string(template_name, context, using=using)
        return HttpResponse(content, content_type=content_type, status=status)

    shortcuts.render_to_response = render_to_response

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcp_server.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
