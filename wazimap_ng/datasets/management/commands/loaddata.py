from django.core.management.base import BaseCommand
from ... import models
import csv

class Command(BaseCommand):
    help = "Load raw data. File expected to contain a Geography with codes and a count column. All other columns will be stuffed into the data column."

    def add_arguments(self, parser):

        parser.add_argument("dataset_id", type=int)
        parser.add_argument("filename", type=str)

        parser.add_argument(
            "--list-datasets",
            action="store_true",
            default=False,
            help="List all datasets. No updates are made."
        )

        parser.add_argument(
            "--encoding",
            action="store_true",
            default="latin1",
            help="File encoding - default is latin1"
        )

    def _get_profile_data(self, levels=None):
        if levels is not None:
            print(f"Loading profiles for: {levels}")
            profiles = models.ProfileData.objects.filter(geography__level__in=levels)
        else:
            print(f"Loading profiles for all levels")
            profiles = models.ProfileData.objects.all()
        print(f"Loaded {len(profiles)} profiles")
        return profiles

    def _list_datasets(self):
        for dataset in models.Dataset.objects.all():
            print(f"{dataset.id}) {dataset.name}")

    def handle(self, *args, **options):

        if options["list_datasets"]:
            self._list_datasets()
        else:
            dataset = models.Dataset.objects.get(pk=options["dataset_id"])
            encoding = options["encoding"]
            cache = {}
            datarows = []
            for idx, row in enumerate(csv.DictReader(open(options["filename"], encoding=encoding))):
                geo_code = row["Geography"]
                del row["Geography"]
                if geo_code in cache:
                    geography = cache[geo_code]
                else:
                    try:
                        geography = models.Geography.objects.get(code=geo_code)
                        cache[geo_code] = geography
                        models.DatasetData.objects.filter(geography=geography, dataset=dataset).delete()
                    except models.Geography.DoesNotExist:
                        print(f"Geography {geo_code} not found - skipping it.")
                        continue
                dd = models.DatasetData(dataset=dataset, geography=geography, data=row)
                datarows.append(dd)
                if len(datarows) >= 10000:
                    print(f"{idx} rows committed")
                    models.DatasetData.objects.bulk_create(datarows, 1000)
                    datarows = []
