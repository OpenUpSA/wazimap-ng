FROM osgeo/gdal:ubuntu-small-3.1.3

RUN apt-get update && apt-get install -y \
  postgresql-client vim less curl apt-transport-https \
  git python3-pip libpq-dev


RUN mkdir -p /config
COPY ./requirements.txt /config
WORKDIR /config
RUN pip3 install -r ./requirements.txt

ENV PYTHONUNBUFFERED 1

COPY ./nginx.conf.d/ /app/nginx.conf.d
COPY ./ /app
WORKDIR /app
RUN rm -rf .git
RUN DJANGO_SECRET_KEY=not-secret-at-build python3 manage.py collectstatic --noinput
CMD ["tail", "-f", "/dev/null"]
