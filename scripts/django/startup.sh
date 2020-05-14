cd /app

python3 manage.py collectstatic --noinput
python3 manage.py migrate 

if [ "$RUN_QCLUSTER" = "Yes" ]
then
    python3 manage.py qcluster& > /var/log/django-q.stdin.log 2> /var/log/django-q.stderr.log
fi

/usr/local/bin/gunicorn wazimap_ng.wsgi --workers=2 -b 0.0.0.0:8000 --forwarded-allow-ips="*" --access-logfile /wazimap-ng.access.log --reload --error-logfile /wazimap-ng.error.log --timeout=300
