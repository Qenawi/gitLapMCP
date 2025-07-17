"""MCP tool definitions."""

from __future__ import annotations

from django_mcp import mcp_app as mcp
import os

from . import gitlab_utils, jira_utils


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


@mcp.tool()
def jira_fetch(
    jql: str,
    *,
    since: str | None = None,
    until: str | None = None,
    start_at: int = 0,
    max_results: int = 50,
    fields: list[str] | None = None,
    include_worklogs: bool = False,
    diff: bool = False,
    export_format: str | None = None,
    file_path: str | None = None,
) -> list[dict[str, object]]:
    """Fetch Jira issues with rich metadata and optional diff/export."""

    issues = jira_utils.fetch_issues(
        jql,
        fields=fields,
        since=since,
        until=until,
        start_at=start_at,
        max_results=max_results,
        include_worklogs=include_worklogs,
    )

    if diff:
        issues = jira_utils.diff_issues(issues, os.path.join(os.getcwd(), "jira_fetch_cache.json"))

    if export_format:
        jira_utils.export_issues(issues, fmt=export_format, path=file_path)

    return issues
