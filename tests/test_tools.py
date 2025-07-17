import asyncio
import sys
from django.test import SimpleTestCase

sys.path.append('clean_mcp_init')

import clean_mcp_init.asgi  # noqa: F401  - ensures application loads
import clean_mcp_init.mcp_tools  # noqa: F401 - registers tools
import django_mcp


class MCPServerTests(SimpleTestCase):
    def test_application_loads(self):
        self.assertIsNotNone(clean_mcp_init.asgi.application)

    def test_tools_registered(self):
        tools = asyncio.run(django_mcp.mcp_app.list_tools())
        names = {t.name for t in tools}
        expected = {
            'add',
            'gitlab_get_merge_requests',
            'gitlab_get_merge_request_comments',
            'gitlab_add_comment',
            'gitlab_pipeline_status',
            'jira_fetch',
        }
        self.assertTrue(expected.issubset(names))
