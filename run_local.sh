# run_local.sh – drop this in the project root and commit it
#!/usr/bin/env bash
set -euo pipefail

# Load every KEY=value pair from .env into the current shell
if [[ -f .env ]]; then
  set -a          # export everything that gets sourced
  source .env     # read the file
  set +a
fi

echo "Starting Django on $HOSTNAME:$PORT …"
python clean_mcp_init/manage.py runserver 0.0.0.0:${PORT:-8000}
