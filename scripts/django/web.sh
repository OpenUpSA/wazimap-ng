#!/bin/bash

cd /app

python3 manage.py migrate --no-input
python3 manage.py collectstatic --no-input
/usr/local/bin/gunicorn wazimap_ng.wsgi --workers=2 -b 0.0.0.0:${PORT:-8000} --forwarded-allow-ips="*"  --reload  --timeout=300
