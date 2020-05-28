#!/bin/bash

cd /app

/usr/local/bin/gunicorn wazimap_ng.wsgi --workers=2 -b 0.0.0.0:8000 --forwarded-allow-ips="*" --access-logfile /wazimap-ng.access.log --reload --error-logfile /wazimap-ng.error.log --timeout=300
