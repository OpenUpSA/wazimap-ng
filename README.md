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