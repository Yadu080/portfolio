#!/usr/bin/env bash
# Build step for hosts like Render/Railway.
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_portfolio   # no-op once content exists
