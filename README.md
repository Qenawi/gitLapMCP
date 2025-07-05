# GitLab MCP Server

This repository contains a lightweight Django JSON-RPC server used to integrate
with GitLab merge request workflows. It exposes several RPC methods that can be
used to list, review and manage merge requests.

## Requirements

- Python 3.10
- GitLab personal access token

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Alternatively, you can use the provided helper script which creates a
virtual environment, installs the dependencies and launches the
development server:

```bash
./setup_and_run.sh
```
## Running the server

Set the following environment variables before starting the server:

- `DJANGO_SECRET_KEY` – secret key for Django (defaults to an insecure value)
- `GITLAB_TOKEN` – personal access token used for the GitLab API
- `GITLAB_URL` – base URL of your GitLab instance (defaults to `https://gitlab.com`)

Start the development server with:

```bash
python manage.py runserver 8000
```

The JSON-RPC endpoint will be available at `http://localhost:8000/rpc/`.

## Continuous Integration

The project includes a GitHub Actions workflow that installs dependencies,
checks the code with `flake8` and runs `django manage.py check`. The workflow is
triggered on every push and pull request to the `main` branch.

## License

This project is licensed under the MIT License.
