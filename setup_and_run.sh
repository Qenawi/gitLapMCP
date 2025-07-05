#!/usr/bin/env bash
set -e

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    python -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
