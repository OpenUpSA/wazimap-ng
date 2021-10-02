import sys

from django.core.management.base import BaseCommand, CommandError

from ...models import Indicator
from django_q.tasks import async_task


class Command(BaseCommand):
    help = 'Rerun indicator data process for variables'

    def handle(self, *args, **options):
        yes = ['y', 'yes', 'ye']
        no = ['no', 'n']
        continue_process = False
        variables = Indicator.objects.all()

        while True:
            confirmation = input(F'Do you want to re run data extraction for {variables.count()} variables? [y/n]').lower()
            if confirmation in no:
                break
            elif confirmation in yes:
                continue_process = True
                break  

        if continue_process:
            for variable in variables:
                async_task(
                    "wazimap_ng.datasets.tasks.indicator_data_extraction",
                    variable,
                    task_name=f"Migration Data Extraction: {variable.id} {variable.name}",
                    hook="wazimap_ng.datasets.hooks.process_task_info",
                    type="data_extraction", assign=False, notify=False
                )
