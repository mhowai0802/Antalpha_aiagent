#!/bin/bash
# Backend setup: create venv and install dependencies
set -e
cd "$(dirname "$0")/.."
echo "Creating virtual environment..."
python -m venv .venv
echo "Activating and installing..."
source .venv/bin/activate
pip install -r requirements.txt
echo "Done. Activate with: source .venv/bin/activate"
