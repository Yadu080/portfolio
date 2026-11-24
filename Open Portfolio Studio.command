#!/bin/bash
# Double-click to open the Portfolio studio (your site's editor) in the browser.
# Keep this window open while you edit; close it when you're done.
cd "$(dirname "$0")"
PY=".venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "First-time setup (takes a minute)…"
  python3 -m venv .venv && "$PY" -m pip install -q -r requirements.txt && "$PY" manage.py migrate -v 0 && "$PY" manage.py seed_portfolio
fi
"$PY" manage.py migrate -v 0
if ! "$PY" manage.py shell -c "from django.contrib.auth import get_user_model as g; import sys; sys.exit(0 if g().objects.filter(is_superuser=True).exists() else 1)"; then
  echo ""
  echo "Create your studio login (you'll use it to sign in):"
  "$PY" manage.py createsuperuser || exit 1
fi
URL="http://127.0.0.1:8000/admin/"
if curl -s -o /dev/null "$URL"; then
  open "$URL"; exit 0
fi
( sleep 2; open "$URL" ) &
echo ""
echo "Studio running at $URL — close this window to stop it."
"$PY" manage.py runserver 127.0.0.1:8000
