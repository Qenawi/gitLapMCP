#!/usr/bin/env bash
set -e

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    python3.10 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

pip install -r requirements.txt

echo "Environment setup complete."
