python3 /app/manage.py collectstatic --noinput
cd /app
exec /usr/local/bin/gunicorn wazimap_ng.wsgi -b 0.0.0.0:8000 --access-logfile /wazimap-ng.access.log --reload --error-logfile /wazimap-ng.error.log
