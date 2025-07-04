import os
import requests
import tempfile
import subprocess
import yaml
import re
from pathlib import Path

from jsonrpc import jsonrpc_method

GITLAB_TOKEN = os.environ.get('GITLAB_TOKEN')
GITLAB_URL = os.environ.get('GITLAB_URL', 'https://gitlab.com')


def gitlab_request(method, endpoint, **kwargs):
    if not GITLAB_TOKEN:
        raise EnvironmentError('GITLAB_TOKEN is not set')
    headers = kwargs.pop('headers', {})
    headers['PRIVATE-TOKEN'] = GITLAB_TOKEN
    url = f"{GITLAB_URL}/api/v4{endpoint}"
    response = requests.request(method, url, headers=headers, **kwargs)
    response.raise_for_status()
    if response.text:
        return response.json()
    return None


@jsonrpc_method('listMergeRequestsOnBranch')
def list_merge_requests_on_branch(request, project_id: str, branch: str):
    params = {
        'source_branch': branch,
        'state': 'opened',
    }
    return gitlab_request(
        'GET',
        f'/projects/{project_id}/merge_requests',
        params=params,
    )


@jsonrpc_method('getMergeRequestChanges')
def get_merge_request_changes(
    request,
    project_id: str,
    merge_request_iid: int,
):
    endpoint = (
        f'/projects/{project_id}/merge_requests/'
        f'{merge_request_iid}/changes'
    )
    return gitlab_request('GET', endpoint)


@jsonrpc_method('addMergeRequestComment')
def add_merge_request_comment(
    request,
    project_id: str,
    merge_request_iid: int,
    body: str,
):
    data = {'body': body}
    endpoint = (
        f'/projects/{project_id}/merge_requests/'
        f'{merge_request_iid}/notes'
    )
    return gitlab_request('POST', endpoint, data=data)


@jsonrpc_method('createMergeRequest')
def create_merge_request(
    request,
    project_id: str,
    source_branch: str,
    target_branch: str,
    title: str,
    description: str = '',
):
    data = {
        'source_branch': source_branch,
        'target_branch': target_branch,
        'title': title,
        'description': description,
    }
    endpoint = f'/projects/{project_id}/merge_requests'
    return gitlab_request('POST', endpoint, data=data)


@jsonrpc_method('approveMergeRequest')
def approve_merge_request(
    request,
    project_id: str,
    merge_request_iid: int,
):
    endpoint = (
        f'/projects/{project_id}/merge_requests/'
        f'{merge_request_iid}/approve'
    )
    return gitlab_request('POST', endpoint)


@jsonrpc_method('getMergeRequestApprovals')
def get_merge_request_approvals(
    request,
    project_id: str,
    merge_request_iid: int,
):
    """Return approvals information for a merge request."""
    endpoint = (
        f'/projects/{project_id}/merge_requests/{merge_request_iid}/approvals'
    )
    return gitlab_request('GET', endpoint)


@jsonrpc_method('getMergeRequestCiStatus')
def get_merge_request_ci_status(
    request,
    project_id: str,
    merge_request_iid: int,
):
    """Return the status of the latest pipeline for a merge request."""
    pipelines = gitlab_request(
        'GET',
        f'/projects/{project_id}/merge_requests/{merge_request_iid}/pipelines',
    )
    if pipelines:
        pipeline_id = pipelines[0].get('id')
        pipeline = gitlab_request(
            'GET',
            f'/projects/{project_id}/pipelines/{pipeline_id}',
        )
        return pipeline.get('status')
    return None


def _write_changes_to_temp(changes, tempdir):
    for change in changes.get('changes', []):
        path = Path(tempdir) / change['new_path']
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            for line in change['diff'].splitlines():
                if line.startswith('+') and not line.startswith('+++'):
                    f.write(line[1:] + '\n')


def _run_flake8(tempdir):
    try:
        completed = subprocess.run(
            ['flake8', '--format=json', str(tempdir)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.stdout:
            return yaml.safe_load(completed.stdout)
    except FileNotFoundError:
        return {}
    return {}


def _run_regex(tempdir, pattern, message):
    results = []
    regex = re.compile(pattern)
    for path in Path(tempdir).rglob('*'):
        if path.is_file():
            with open(path) as f:
                for idx, line in enumerate(f, start=1):
                    if regex.search(line):
                        results.append({
                            'path': str(path.relative_to(tempdir)),
                            'line': idx,
                            'message': message,
                        })
    return results


@jsonrpc_method('reviewMergeRequest')
def review_merge_request(request, project_id: str, merge_request_iid: int):
    changes = get_merge_request_changes(request, project_id, merge_request_iid)
    comments = []
    with tempfile.TemporaryDirectory() as tmp:
        _write_changes_to_temp(changes, tmp)
        with open(Path(__file__).resolve().parent.parent / 'rules.yml') as f:
            rules = yaml.safe_load(f).get('rules', [])
        for rule in rules:
            if rule.get('linter') == 'flake8':
                flake8_output = _run_flake8(tmp)
                for file_path, messages in flake8_output.items():
                    for m in messages:
                        comments.append({
                            'file_path': file_path,
                            'line': m.get('line'),
                            'body': m.get('text'),
                        })
            elif rule.get('type') == 'regex':
                regex_comments = _run_regex(
                    tmp,
                    rule.get('pattern'),
                    rule.get('message', ''),
                )
                for c in regex_comments:
                    comments.append({
                        'file_path': c['path'],
                        'line': c['line'],
                        'body': c['message'],
                    })
    return comments
