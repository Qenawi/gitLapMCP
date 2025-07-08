"""Utility helpers for interacting with the GitLab API."""

from __future__ import annotations

import os
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ────────── fallback shim for environments without "requests" ──────────
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    import json
    from urllib import request as urllib_request

    class _Resp:
        def __init__(self, resp: urllib_request.addinfourl):
            self._resp = resp
            self.status_code = resp.getcode()

        def json(self):
            return json.loads(self._resp.read().decode())

        def raise_for_status(self):
            if not (200 <= self.status_code < 300):
                raise ValueError(f"HTTP {self.status_code}")

    def _http_call(method: str, url: str, *, headers=None, data=None, params=None):
        if params:
            import urllib.parse
            url += "?" + urllib.parse.urlencode(params)
        req = urllib_request.Request(
            url, data=data, headers=headers or {}, method=method.upper()
        )
        return _Resp(urllib_request.urlopen(req))

    class requests:  # type: ignore
        @staticmethod
        def get(url, headers=None, params=None):
            return _http_call("GET", url, headers=headers, params=params)

        @staticmethod
        def post(url, headers=None, json=None):
            data = None
            if json is not None:
                data = (
                    json.__class__.__name__ != "str"
                    and bytes(__import__("json").dumps(json), "utf-8")
                    or json
                )
                headers = headers or {}
                headers.setdefault("Content-Type", "application/json")
            return _http_call("POST", url, headers=headers, data=data)

# ───────────────────────────────────────────────────────────────────────

GITLAB_API_URL = os.environ.get("GITLAB_API_URL", "https://gitlab.com/api/v4")
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")


def _headers() -> dict[str, str]:
    hdrs: dict[str, str] = {}
    if GITLAB_TOKEN:
        hdrs["PRIVATE-TOKEN"] = GITLAB_TOKEN
    return hdrs


# ────────── Merge-request helpers ──────────
def get_merge_requests(project_id: int, branch_name: str) -> list[dict[str, Any]]:
    """Return merge requests for the given branch name."""
    url = f"{GITLAB_API_URL}/projects/{project_id}/merge_requests"
    params = {"source_branch": branch_name}

    logger.debug("GET %s params=%s", url, params)
    resp = requests.get(url, headers=_headers(), params=params)
    resp.raise_for_status()

    data = resp.json()
    logger.info(
        "Fetched %d merge requests for project=%s branch=%s",
        len(data),
        project_id,
        branch_name,
    )
    return data


def get_merge_request_comments(project_id: int, mr_iid: int) -> list[dict[str, Any]]:
    """Return all comments for a merge request."""
    url = f"{GITLAB_API_URL}/projects/{project_id}/merge_requests/{mr_iid}/notes"
    logger.debug("GET %s", url)

    resp = requests.get(url, headers=_headers())
    resp.raise_for_status()

    data = resp.json()
    logger.info(
        "Fetched %d comments for project=%s MR=%s",
        len(data),
        project_id,
        mr_iid,
    )
    return data


def add_merge_request_comment(project_id: int, mr_iid: int, body: str) -> dict[str, Any]:
    """Add a comment to a merge request."""
    url = f"{GITLAB_API_URL}/projects/{project_id}/merge_requests/{mr_iid}/notes"
    logger.debug('POST %s body="%s"', url, body[:60])

    resp = requests.post(url, headers=_headers(), json={"body": body})
    resp.raise_for_status()

    data = resp.json()
    logger.info("Posted comment to project=%s MR=%s", project_id, mr_iid)
    return data


def get_merge_request_pipeline_status(
    project_id: int, mr_iid: int
) -> Optional[str]:
    """Return the status of the latest pipeline for a merge request."""
    url = f"{GITLAB_API_URL}/projects/{project_id}/merge_requests/{mr_iid}/pipelines"
    logger.debug("GET %s", url)

    resp = requests.get(url, headers=_headers())
    resp.raise_for_status()

    pipelines = resp.json()
    status = pipelines[0].get("status") if pipelines else None
    logger.info(
        "Latest pipeline status for project=%s MR=%s is %s",
        project_id,
        mr_iid,
        status,
    )
    return status
