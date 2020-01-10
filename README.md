# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)  

# Local Development

Start the dev server for local development:
```bash
docker-compose up
```

Load up the database

```bash
docker exec wazimap-ng-db createdb -U postgres wazimap_ng
curl https://wazimap-ng.s3-eu-west-1.amazonaws.com/wazimap-ng.dump-20200108.gz | gunzip -c | docker exec -i wazimap-ng-db pg_restore -U postgres -d wazimap_ng
```

# Production
The code uses the python pg_trgm extension. 0001_initial.py in the extensions app loads that extension in the database. If your database user does not have superuser permissions, this migration will fail. Setting the DJANGO_INSTALL_EXTENSIONS environment variable to False [default] will prevent this extension from being loaded.