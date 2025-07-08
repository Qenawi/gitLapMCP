# Clean MCP Init

This repository contains a minimal Django project configured with FastMCP.
It exposes a handful of MCP tools including a simple `add` example and a few
helpers for interacting with the GitLab API.  See `clean_mcp_init/mcp_tools.py`
for the tool definitions.

## Development

Install requirements and run the tests:

```bash
pip install -r clean_mcp_init/requirements.txt
python clean_mcp_init/manage.py test
```

The ASGI application is defined in `clean_mcp_init/asgi.py` and mounts the
MCP server at `/mcp`.
