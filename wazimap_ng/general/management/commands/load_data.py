from django.core.management.base import BaseCommand, CommandError

from wazimap_ng.datasets.models import Dataset, Geography
from wazimap_ng.profile.models import Profile

from tests.datasets.factories import DatasetFactory, DatasetFileFactory, GeographyFactory, GeographyHierarchyFactory
from tests.boundaries.factories import GeographyBoundaryFactory
from tests.profile.factories import ProfileFactory

from django_q.tasks import async_task

class Command(BaseCommand):
    help = "loads initial data for local setup and PR review apps"

    def get_profile(self, geo_code="ZA"):
        geo = Geography.objects.get(code=geo_code)
        geo_h = GeographyHierarchyFactory(name="South Africa", root_geography=geo)
        return ProfileFactory(name="Main Profile", geography_hierarchy=geo_h)

    def dataset(self, name, profile, path):
        dataset = DatasetFactory(name=name, profile=profile)
        df = DatasetFileFactory(document__from_path=path, dataset_id=dataset.pk)
        task = async_task(
            "wazimap_ng.datasets.tasks.process_uploaded_file",
            df, dataset,
            hook="wazimap_ng.datasets.hooks.process_task_info",
            task_name=f"Uploading data: {dataset.name}",
            type="upload", assign=True
        )

    def handle(self, *args, **options):
        try:
            profile = self.get_profile()
            self.dataset("Population Estimates", profile, "fixtures/population_estimates.csv")
            self.dataset("Race", profile, "fixtures/population_group_age_group.csv")
        except Exception as e:
            print(e)
        return ""

