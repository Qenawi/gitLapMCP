# clean_mcp_init/mcp_tools.py
from django_mcp import mcp_app as mcp   # same FastMCP instance the ASGI app uses

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b