This is the backend for Wazimap-NG.

# Introduction

Wazimap-NG is the next version of [Wazimap](http://www.wazimap.co.za). It provides a platform for users to bind tabular data to spatial boundaries in order create curated views of datasets. Yes - that's probably too vague a description to understand what it is. Hopefully the images below provide a better description:

<a href="https://postimg.cc/G8XkZRhV" target="_blank"><img src="https://i.postimg.cc/G8XkZRhV/Screen-Shot-2020-09-27-at-09-50-00.png" alt="Screen-Shot-2020-09-27-at-09-50-00"/></a> <a href="https://postimg.cc/MM67PHx1" target="_blank"><img src="https://i.postimg.cc/MM67PHx1/Screen-Shot-2020-09-27-at-09-50-33.png" alt="Screen-Shot-2020-09-27-at-09-50-33"/></a><br/><br/>
<a href="https://postimg.cc/4HnzG0Yd" target="_blank"><img src="https://i.postimg.cc/4HnzG0Yd/Screen-Shot-2020-09-27-at-09-50-50.png" alt="Screen-Shot-2020-09-27-at-09-50-50"/></a> <a href="https://postimg.cc/MXsDL7nH" target="_blank"><img src="https://i.postimg.cc/MXsDL7nH/Screen-Shot-2020-09-27-at-09-51-30.png" alt="Screen-Shot-2020-09-27-at-09-51-30"/></a><br/><br/>

See a link to the beta site here: [https://beta.youthexplorer.org.za](https://beta.youthexplorer.org.za).

You can find the backend code in this repository. The frontend is available here: [https://github.com/openupsa/wazimap-ng-ui](https://github.com/openupsa/wazimap-ng-ui).

# New features

The main new features are:

* Admins now have more flexibility when it comes to loading data. This includes uploading massive datasets and then slicing and dicing in the backend rather than pre-preparing datasets beforehand.
* Point data is now fully integrated as a first-class spatial object.
* Choropleths built into the main view. These were hidden behind multiple clicks in the previous version.
* One platform can host multiple profiles off the same database.
* The Rich data view allows richer disaggregation of indicators.
* The administrator can configure the view to use custom basemaps, colours, and other UI settings.
* Arbitrary spatial boundaries and hierarchies can be loaded onto the same server.
* Toggling of overlapping boundary layers such as switching between wards and mainplaces which typically cover the same areas.
* Integration into third-party data sources for realtime data feeds.

# Related software
There is no shortage of mapping software available, both commerical and open-source. Wazimap focuses on providing a platform for data custodians to showcase their datasets and mashing them up with public data. The most similar tool that we have found is the excellent [GeoNode](https://geonode.org/). We feel that approach to publishing data is significantly different enough to warrant a separate project.

# Roadmap
Version 0.8 is due soon and will fix bugs that currently don't have workarounds. We'll publish the 1.0 roadmap soon.

# Future features
* WFS endpoint for publishing data to other GIS software
* Pluggable data visualisations
* Better handling of geography hierarchies.
* Improved handling of temporal and other types of non-census-like data.
* Speed improvements
* A large standard database of public datasets.

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)

# Local Development

Local development is normally done inside docker-compose so that the supporting services are available and the environment is very similar to how the application is run in production.

Make docker-compose start the supporting services

    docker-compose run --rm web python wait_for_postgres.py

Migrate, load development data and start the app

    docker-compose run --rm web python manage.py migrate
    docker-compose run --rm web python manage.py loaddata demodata.json
    docker-compose up

Run the tests

    docker-compose run --rm -e DJANGO_CONFIGURATION=Test web pytest /app/tests

Run Django manage commands inside docker-compose, e.g. create a superuser:

    docker-compose run --rm web python manage.py createsuperuser


# Demo data

Demo data should consist of the smallest amount of data needed to demonstrate as
much functionality as possible with the minimum effort. Updates to demo data should
aim to keep diffs as small as possible as well.

The demo data creates a superuser with username `admin`. Ask for the password
in the dev channel or update it using `manage.py changepassword` or
`manage.py createsuperuser`.

Use the following command to generate demo data, diff to check that the change
looks sane before committing. Update the command here if changes are needed.

```
docker-compose run --rm web python -Wi manage.py dumpdata \
  --indent 2 \
  --natural-foreign \
  profile \
  auth.group \
  auth.user \
  guardian \
  datasets \
  boundaries.geographyboundary \
  points.category \
  points.location \
  points.profilecategory \
  points.theme \
  general.metadata \
    > demodata.json
```

Configuration is done via environment variables.

*** [Avoid creating/using variables that define an environment](https://12factor.net/) ***. Instead of creating a variable DEV or TEST or PROD and then writing code like `if TEST`, rather make each feature/backing service configurable, and configure them as needed in each environment.

Ensure variable defaults are safe if someone forgot to set them in production. Variables that absolutely must be set in each environment can be left without a default so that the app only starts when configured properly.

| Key | Default | Type | Description |
|-----|---------|------|-------------|
| `DATABASE_URL` | undefined | String | `postgresql://user:password@hostname/dbname` style URL |
| `DJANGO_DEBUG_TOOLBAR` | False | Boolean | Set to `True` to enable the Django Debug toolbar NOT ON A PUBLIC SERVER! |
| `DJANGO_SECRET_KEY` | undefined | String | Set this to something secret and unguessable in production. The security of your cookies and other crypto stuff in django depends on it. |
| `EMAIL_BACKEND` | django.core.mail.backends.smtp.EmailBackend |||
| `DEFAULT_FILE_STORAGE` | undefined | string | e.g. `storages.backends.s3boto3.S3Boto3Storage` or `django.core.files.storage.FileSystemStorage` |
| `AWS_ACCESS_KEY_ID` ||| Only required if `DEFAULT_FILE_STORAGE` is `storages.backends.s3boto3.S3Boto3Storage` |
| `AWS_SECRET_ACCESS_KEY` ||| ditto |
| `AWS_STORAGE_BUCKET_NAME` ||| ditto |
| `AWS_S3_REGION_NAME` ||| ditto |
| `DJANGO_Q_SYNC` | False || Usually useful for automated tests |
| `ENVIRONMENT_NAME` ||| Only to be used for a server to identify itself e.g. in logs or notifications, and not intended for configuration logic |
| `DEBUG_CACHE` | False | boolean | Set to true enable the cache despite DEBUG being true. This is useful when you want the cache enabled for development. |


# Documentation
These are works in progress:

* [Technical manual](https://openup.gitbook.io/wazi-ng-technical/)
* [Administrator manual](https://openup.gitbook.io/wazimap-ng/)

# Contributions
Contributions are welcome - we are working towards making this process easier. New development takes place in the [staging branch](https://github.com/OpenUpSA/wazimap-ng/tree/staging)

# Shoulders of giants
This project is the next iteration of a number of excellent projects starting with [CensusReporter](https://censusreporter.org/) and [Wazimap](http://www.wazimap.co.za) that followed it. Special thanks to William Bird from [Media Monitoring Africa](https://mediamonitoringafrica.org) whose initial idea (and funding) it was to build a tool to help journalists better understand areas they were reporting on. Also thanks to Chris Berens from [VPUU](vpuu.org.za) who directed funding to help kickstart this new build. Finally, all of the amazing spatial software and tools developed by one of the most dedicated open source communities out there.
