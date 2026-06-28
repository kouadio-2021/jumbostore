#!/bin/bash
# Lance le backend JUMBOSTORE en local pour développement/test.
set -e
cd "$(dirname "$0")"
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
