cd /app

python3 manage.py collectstatic --noinput
python3 manage.py migrate 
/usr/local/bin/gunicorn wazimap_ng.wsgi -b 0.0.0.0:8000 --forwarded-allow-ips="*" --access-logfile /wazimap-ng.access.log --reload --error-logfile /wazimap-ng.error.log
