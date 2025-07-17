"""Utility helpers for interacting with the Jira REST API."""

from __future__ import annotations

import base64
import json
import logging
import os
from typing import Any, Iterable, Optional

logger = logging.getLogger(__name__)

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    import json as _json
    from urllib import request as urllib_request

    class _Resp:
        def __init__(self, resp: urllib_request.addinfourl):
            self._resp = resp
            self.status_code = resp.getcode()

        def json(self):
            return _json.loads(self._resp.read().decode())

        def raise_for_status(self):
            if not (200 <= self.status_code < 300):
                raise ValueError(f"HTTP {self.status_code}")

    def _http_call(method: str, url: str, *, headers=None, data=None, params=None):
        if params:
            import urllib.parse
            url += "?" + urllib.parse.urlencode(params)
        req = urllib_request.Request(url, data=data, headers=headers or {}, method=method.upper())
        return _Resp(urllib_request.urlopen(req))

    class requests:  # type: ignore
        @staticmethod
        def get(url, headers=None, params=None, auth=None):
            return _http_call("GET", url, headers=headers, params=params)

# ----------------------------------------------------------------------------

JIRA_API_URL = os.environ.get("JIRA_API_URL", "https://your-jira.example.com")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")
JIRA_TOKEN = os.environ.get("JIRA_TOKEN")


def _auth_header() -> dict[str, str]:
    if JIRA_EMAIL and JIRA_TOKEN:
        token = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()
        return {"Authorization": f"Basic {token}"}
    return {}


def _headers() -> dict[str, str]:
    hdrs = {"Accept": "application/json"}
    hdrs.update(_auth_header())
    return hdrs


# ----------------------------------------------------------------------------

def fetch_issues(
    jql: str,
    *,
    fields: Optional[Iterable[str]] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    start_at: int = 0,
    max_results: int = 50,
    include_comments: bool = True,
    include_worklogs: bool = False,
    include_attachments: bool = True,
) -> list[dict[str, Any]]:
    """Fetch issues from Jira matching the given JQL."""

    query = jql
    date_clauses = []
    if since:
        date_clauses.append(f'updated >= "{since}"')
    if until:
        date_clauses.append(f'updated <= "{until}"')
    if date_clauses:
        if query:
            query = f"({query}) and {' and '.join(date_clauses)}"
        else:
            query = " and ".join(date_clauses)

    search_url = f"{JIRA_API_URL}/rest/api/3/search"

    requested_fields = set(fields or [])
    base_fields = {
        "key",
        "summary",
        "status",
        "updated",
        "description",
        "reporter",
        "assignee",
        "priority",
    }
    if include_comments:
        base_fields.add("comment")
    if include_worklogs:
        base_fields.add("worklog")
    if include_attachments:
        base_fields.add("attachment")
    if requested_fields:
        base_fields.update(requested_fields)

    params = {
        "jql": query,
        "startAt": start_at,
        "maxResults": max_results,
        "fields": ",".join(sorted(base_fields)),
        "expand": "changelog",
    }
    logger.debug("GET %s params=%s", search_url, params)

    resp = requests.get(search_url, headers=_headers(), params=params)
    resp.raise_for_status()
    data = resp.json()

    results: list[dict[str, Any]] = []
    for issue in data.get("issues", []):
        parsed = _parse_issue(issue, include_comments, include_worklogs, include_attachments)
        results.append(parsed)

    logger.info("Fetched %d issues", len(results))
    return results


def _parse_issue(issue: dict[str, Any], include_comments: bool, include_worklogs: bool, include_attachments: bool) -> dict[str, Any]:
    fields = issue.get("fields", {})
    parsed = {
        "key": issue.get("key"),
        "summary": fields.get("summary"),
        "status": fields.get("status", {}).get("name") if isinstance(fields.get("status"), dict) else fields.get("status"),
        "updated": fields.get("updated"),
        "description": fields.get("description"),
        "reporter": fields.get("reporter", {}).get("displayName") if isinstance(fields.get("reporter"), dict) else fields.get("reporter"),
        "assignee": fields.get("assignee", {}).get("displayName") if isinstance(fields.get("assignee"), dict) else fields.get("assignee"),
        "priority": fields.get("priority", {}).get("name") if isinstance(fields.get("priority"), dict) else fields.get("priority"),
    }

    if include_comments and fields.get("comment"):
        comments = fields["comment"].get("comments", [])
        comments = sorted(comments, key=lambda c: c.get("created"), reverse=True)[:3]
        parsed["comments"] = [
            {
                "author": c.get("author", {}).get("displayName"),
                "created": c.get("created"),
                "body": c.get("body"),
            }
            for c in comments
        ]

    if include_worklogs and fields.get("worklog"):
        parsed["worklogs"] = [
            {
                "author": w.get("author", {}).get("displayName"),
                "timeSpent": w.get("timeSpent"),
                "created": w.get("created"),
            }
            for w in fields["worklog"].get("worklogs", [])
        ]

    if include_attachments and fields.get("attachment"):
        parsed["attachments"] = [
            {
                "filename": a.get("filename"),
                "author": a.get("author", {}).get("displayName"),
                "created": a.get("created"),
            }
            for a in fields["attachment"]
        ]

    parsed["status_history"] = []
    changelog = issue.get("changelog", {})
    for history in changelog.get("histories", []):
        author = history.get("author", {}).get("displayName")
        created = history.get("created")
        for item in history.get("items", []):
            if item.get("field") == "status":
                parsed["status_history"].append(
                    {
                        "from": item.get("fromString"),
                        "to": item.get("toString"),
                        "at": created,
                        "by": author,
                    }
                )

    return parsed


# ----------------------------------------------------------------------------

def diff_issues(new: list[dict[str, Any]], cache_path: str) -> list[dict[str, Any]]:
    """Return only issues whose payload changed since last cache."""
    changed = []
    old_map: dict[str, Any] = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as fh:
                old = json.load(fh)
            old_map = {issue.get("key"): issue for issue in old}
        except Exception as exc:  # pragma: no cover - corrupted cache
            logger.warning("Failed to read cache: %s", exc)

    for issue in new:
        key = issue.get("key")
        if issue != old_map.get(key):
            changed.append(issue)

    try:
        with open(cache_path, "w", encoding="utf-8") as fh:
            json.dump(new, fh, indent=2)
    except Exception as exc:  # pragma: no cover - write failures
        logger.warning("Failed to write cache: %s", exc)

    return changed


# ----------------------------------------------------------------------------

def export_issues(issues: list[dict[str, Any]], *, fmt: str, path: Optional[str] = None) -> str | None:
    """Export issues to JSON or CSV. Returns string if no path provided."""
    fmt = fmt.lower()
    if fmt not in {"json", "csv"}:
        raise ValueError("fmt must be 'json' or 'csv'")

    if fmt == "json":
        payload = json.dumps(issues, indent=2)
        if path:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(payload)
            return None
        return payload

    # CSV export
    import csv
    if not issues:
        csv_data = ""
    else:
        fieldnames = sorted({k for issue in issues for k in issue.keys()})
        from io import StringIO
        buf = StringIO()
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        for issue in issues:
            writer.writerow(issue)
        csv_data = buf.getvalue()

    if path:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(csv_data)
        return None
    return csv_data

