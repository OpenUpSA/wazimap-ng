import os
import sys
from pathlib import Path

import django
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db.transaction import atomic
from django_q.tasks import async_task

from wazimap_ng.datasets.models import Dataset, DatasetFile
from wazimap_ng.profile.models import Profile


class Command(BaseCommand):
    help = 'Uploads a dataset from the command line. '

    def add_arguments(self, parser):
        parser.add_argument('profile_name', type=str, help="Name of profile as it exists in the database (case sensisitve).")
        parser.add_argument('dataset_name', type=str, help="This is the name that will be used for the dataset.")
        parser.add_argument('filename', type=str, help="Path to the file to be uploaded.")

    def load_file(self, profile, dataset_name, path):
        with atomic():
            dataset = Dataset.objects.create(profile=profile, name=dataset_name, geography_hierarchy=profile.geography_hierarchy)
            df = DatasetFile.objects.create(name=dataset_name, dataset_id=dataset.pk, document=File(path.open("rb")))

            uuid = task = async_task(
                "wazimap_ng.datasets.tasks.process_uploaded_file",
                df, dataset,
                task_name=f"Uploading data from command: {dataset.name}",
                hook="wazimap_ng.datasets.hooks.process_task_info",
                key="No session",
                type="upload", assign=True, notify=False
            )

            return uuid

    def handle(self, *args, **options):
        profile_name = options["profile_name"]
        dataset_name = options["dataset_name"]
        filename = options["filename"]
        path = Path(filename)

        if not path.exists():
            raise CommandError(f'Could not find data file at {filename}')

        try:
            profile = Profile.objects.get(name=profile_name)
            uuid = self.load_file(profile, dataset_name, path)

        except Profile.DoesNotExist:
            profiles = ", ".join(p.name for p in Profile.objects.all())
            raise CommandError(f'Profile {profile_name} does not exist. The following profiles are available: {profiles}')

        self.stdout.write(f"Task submitted successfully with uuid: {uuid}")
