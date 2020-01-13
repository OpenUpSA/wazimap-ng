cd /app
git clone https://github.com/OpenUpSA/wazimap-ng.git


python3 manage.py collectstatic --noinput
exec /usr/local/bin/gunicorn wazimap_ng.wsgi -b 0.0.0.0:5000 --access-logfile /wazimap-ng.access.log --reload --error-logfile /wazimap-ng.error.log
