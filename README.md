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

Set the environment variables
export DATABASE_URL=postgis://wazimap_ng:wazimap_ng@localhost:5432/wazimap_ng
export DJANGO_SECRET_KEY=ffsrwerefdsfweffs

# Install GDAL for geodjango
On a mac
```bash
brew install gdal
```

or some variation of apt-get for Ubuntu

```bash
pip install pygdal==$(gdal-config --version)
```

Note: you may get an error that says

Could not find a version that satisfies the requirement pygdal==1.11.3 (from versions: 1.8.1.0, 1.8.1.1, 1.8.1.2, 1.8.1.3, 1.9.2.0, 1.9.2.1, 1.9.2.3, 1.10.0.0, 1.10.0.1, 1.10.0.3, 1.10.1.0, 1.10.1.1, 1.10.1.3, 1.11.0.0, 1.11.0.1, 1.11.0.3, 1.11.1.0, 1.11.1.1, 1.11.1.3, 1.11.2.1, 1.11.2.3, 1.11.3.3, 1.11.4.3, 2.1.0.3) No matching distribution found for pygdal==1.11.3
If that happens, run the pip install again but with the highest version that still matches. e.g. in this case you would run pip install pygdal==1.11.3.3