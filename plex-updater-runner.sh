#!/bin/bash
VENV_DIR="/opt/scripts/pyupdater-plex/venv"
PYTHON_SCRIPT="/opt/scripts/pyupdater-plex/updater.py"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
    source "$VENV_DIR/bin/activate"
    pip install requests pyyaml
fi

source "$VENV_DIR/bin/activate"
python3 "$PYTHON_SCRIPT"
deactivate