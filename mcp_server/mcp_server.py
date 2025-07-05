import json
import sys
from typing import Any, Dict, Callable

from mcp import Application, tool, run_stdio

from mcp_server.api.api import (
    list_merge_requests_on_branch,
    get_merge_request_changes,
    add_merge_request_comment,
    create_merge_request,
    approve_merge_request,
    get_merge_request_approvals,
    get_merge_request_ci_status,
    review_merge_request,
)


def _wrap_result(data: Any) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(data)}]}


app = Application()


@tool(
    name="list_merge_requests_on_branch",
    description="List all open merge requests for a specific branch",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "branch": {"type": "string"},
        },
        "required": ["project_id", "branch"],
    },
)
def t_list_merge_requests_on_branch(project_id: str, branch: str):
    result = list_merge_requests_on_branch(None, project_id, branch)
    return _wrap_result(result)


@tool(
    name="get_merge_request_changes",
    description="Get the changes for a specific merge request",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "merge_request_iid": {"type": "string"},
        },
        "required": ["project_id", "merge_request_iid"],
    },
)
def t_get_merge_request_changes(project_id: str, merge_request_iid: str):
    result = get_merge_request_changes(None, project_id, merge_request_iid)
    return _wrap_result(result)


@tool(
    name="add_merge_request_comment",
    description="Add a comment to a merge request",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "merge_request_iid": {"type": "string"},
            "body": {"type": "string"},
        },
        "required": ["project_id", "merge_request_iid", "body"],
    },
)
def t_add_merge_request_comment(project_id: str, merge_request_iid: str, body: str):
    result = add_merge_request_comment(None, project_id, merge_request_iid, body)
    return _wrap_result(result)


@tool(
    name="create_merge_request",
    description="Create a new merge request",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "source_branch": {"type": "string"},
            "target_branch": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
        },
        "required": ["project_id", "source_branch", "target_branch", "title"],
    },
)
def t_create_merge_request(
    project_id: str,
    source_branch: str,
    target_branch: str,
    title: str,
    description: str = "",
):
    result = create_merge_request(
        None,
        project_id,
        source_branch,
        target_branch,
        title,
        description,
    )
    return _wrap_result(result)


@tool(
    name="approve_merge_request",
    description="Approve a merge request",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "merge_request_iid": {"type": "string"},
        },
        "required": ["project_id", "merge_request_iid"],
    },
)
def t_approve_merge_request(project_id: str, merge_request_iid: str):
    result = approve_merge_request(None, project_id, merge_request_iid)
    return _wrap_result(result)


@tool(
    name="get_merge_request_approvals",
    description="Get approval information for a merge request",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "merge_request_iid": {"type": "string"},
        },
        "required": ["project_id", "merge_request_iid"],
    },
)
def t_get_merge_request_approvals(project_id: str, merge_request_iid: str):
    result = get_merge_request_approvals(None, project_id, merge_request_iid)
    return _wrap_result(result)


@tool(
    name="get_merge_request_ci_status",
    description="Get the CI/CD pipeline status for a merge request",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "merge_request_iid": {"type": "string"},
        },
        "required": ["project_id", "merge_request_iid"],
    },
)
def t_get_merge_request_ci_status(project_id: str, merge_request_iid: str):
    result = get_merge_request_ci_status(None, project_id, merge_request_iid)
    return _wrap_result(result)


@tool(
    name="review_merge_request",
    description="Perform automated code review on a merge request",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "merge_request_iid": {"type": "string"},
        },
        "required": ["project_id", "merge_request_iid"],
    },
)
def t_review_merge_request(project_id: str, merge_request_iid: str):
    result = review_merge_request(None, project_id, merge_request_iid)
    return _wrap_result(result)


if __name__ == "__main__":
    run_stdio(app)
