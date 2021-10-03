#!/bin/bash

cd /app

/usr/local/bin/gunicorn wazimap_ng.wsgi --workers=2 -b 0.0.0.0:${PORT:-8000} --forwarded-allow-ips="*"  --reload  --timeout=300
