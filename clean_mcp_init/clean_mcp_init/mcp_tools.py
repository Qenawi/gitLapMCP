"""MCP tool definitions."""

from __future__ import annotations

from django_mcp import mcp_app as mcp

from . import gitlab_utils


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b


@mcp.tool()
def gitlab_get_merge_requests(project_id: int, branch_name: str):
    """Return merge requests for a branch."""
    return gitlab_utils.get_merge_requests(project_id, branch_name)


@mcp.tool()
def gitlab_get_merge_request_comments(project_id: int, merge_request_iid: int):
    """Return comments for a merge request."""
    return gitlab_utils.get_merge_request_comments(project_id, merge_request_iid)


@mcp.tool()
def gitlab_add_comment(project_id: int, merge_request_iid: int, body: str):
    """Add a comment to a merge request."""
    return gitlab_utils.add_merge_request_comment(project_id, merge_request_iid, body)


@mcp.tool()
def gitlab_pipeline_status(project_id: int, merge_request_iid: int):
    """Return the latest pipeline status for a merge request."""
    return gitlab_utils.get_merge_request_pipeline_status(project_id, merge_request_iid)
