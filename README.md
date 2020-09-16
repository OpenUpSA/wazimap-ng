# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)

# Local Development

Start the dev server for local development. Before you've created your database, the webserver will break because it can't find the database.
```bash
docker-compose up
```

curl https://wazimap-ng.s3-eu-west-1.amazonaws.com/wazimap_ng-2020203.bak.gz | gunzip -c | docker exec -i wazimap-ng_db_1 pg_restore -U postgres -d wazimap_ng
```

If this is the first time you're running this, bring the containers down, then up again
```bash
docker-compose down
docker-compose up
```

# Production
To build a new image:

```bash
./scripts/docker_build.sh
```

Note, this currently logs into adieyal on docker-hub. This will be moved to the OpenUp account in future.

<!-- Set the environment variables
export DATABASE_URL=postgis://wazimap_ng:wazimap_ng@localhost:5432/wazimap_ng
export DJANGO_SECRET_KEY=ffsrwerefdsfweffs
 -->
<!-- # Install GDAL for geodjango
On a mac
```bash
brew install gdal
 -->```

<!-- or some variation of apt-get for Ubuntu

then

```bash
pip install pygdal==$(gdal-config --version)
```

Note: you may get an error that says

Could not find a version that satisfies the requirement pygdal==1.11.3 (from versions: 1.8.1.0, 1.8.1.1, 1.8.1.2, 1.8.1.3, 1.9.2.0, 1.9.2.1, 1.9.2.3, 1.10.0.0, 1.10.0.1, 1.10.0.3, 1.10.1.0, 1.10.1.1, 1.10.1.3, 1.11.0.0, 1.11.0.1, 1.11.0.3, 1.11.1.0, 1.11.1.1, 1.11.1.3, 1.11.2.1, 1.11.2.3, 1.11.3.3, 1.11.4.3, 2.1.0.3) No matching distribution found for pygdal==1.11.3
If that happens, run the pip install again but with the highest version that still matches. e.g. in this case you would run pip install pygdal==1.11.3.3


GDAL installation errors are generally a result of mismatched versions between the python library and the system libraries. Ensure that you are installing the correct versions. If you are using dokku/heroku with the heroku geo buildpack, you should consult https://github.com/heroku/heroku-geo-buildpack - the default version of gdal is 2.4.0 at the time of writing.

## Note when installing with the Heroku geo buildpack

The Heroku geo buildpack installs the library in /app/.heroku-geo-buildpack/vendor. In order for pygdal to find it, you need to set the follow environment variables

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/app/.heroku-geo-buildpack/vendor/bin/
GDALHOME=/app/.heroku-geo-buildpack/vendor/

On dokku you would run the following
```bash
dokku config:set wazimap-ng --no-restart PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/app/.heroku-geo-buildpack/vendor/bin/
dokku config:set wazimap-ng --no-restart GDALHOME=/app/.heroku-geo-buildpack/vendor/ -->




Some notes for database migration - will turn this into proper documentation in the future

SELECT 'ALTER TABLE '|| schemaname || '.' || tablename ||' OWNER TO wazimap_ng;'
FROM pg_tables WHERE NOT schemaname IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename;
