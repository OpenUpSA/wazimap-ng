import sys

from django.core.management.base import BaseCommand, CommandError

from ...models import Indicator
from django.contrib.auth.models import User
from django_q.tasks import async_task
from django_q.brokers import get_broker
from django_q.models import Task


class Command(BaseCommand):
    help = 'Rerun indicator data process for variables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--variables', nargs='+', type=int, default=[],
            help="pass variable ids to process : --variables 1 2 3"
        )
        parser.add_argument(
            '--datasets', nargs='+', type=int, default=[],
            help="pass dataset ids to process linked variables : --datasets 1 2 3"
        )
        parser.add_argument(
            '--profiles', nargs='+', type=int, default=[],
            help="pass profile ids to process linked variables : --profiles 1 2 3"
        )
        parser.add_argument(
            '--user_id', nargs=1, type=int,
            help="pass user id to get fail task notification : --user_id 2"
        )
        parser.add_argument(
            '--rerun_failed', nargs=1, type=int,
            help="rerun all failed tasks for extraction-ID group : --rerun_failed 20"
        )


    def handle(self, *args, **options):
        to_update = options['variables']
        datasets = options['datasets']
        profiles = options['profiles']
        user_id = options['user_id']
        rerun_failed = options['rerun_failed']
        email_on_fail = True if user_id else False
        user = None

        if user_id:
            user_id = user_id[0]
            user = User.objects.filter(id=user_id).first()
            if not user:
                print(F"User with user id {user_id} does not exist")
                sys.exit()

        if datasets:
            to_update = list(Indicator.objects.filter(
                dataset_id__in=datasets
            ).values_list("id", flat=True)) + to_update

        if profiles:
            to_update = list(Indicator.objects.filter(
                dataset__profile_id__in=profiles
            ).values_list("id", flat=True)) + to_update

        if rerun_failed:
            to_update = to_update + [t.args[0].id for t in Task.objects.filter(
                group=f"extraction-{rerun_failed[0]}", success=False
            )]

        variables = Indicator.objects.all()
        if to_update:
            variables = variables.filter(
                id__in=list(set(to_update))
            )

        yes = ['y', 'yes', 'ye']
        no = ['no', 'n']
        continue_process = False

        while True:
            confirmation = input(F'Do you want to re run data extraction for {variables.count()} variables? [y/n]').lower()
            if confirmation in no:
                break
            elif confirmation in yes:
                continue_process = True
                break  

        if continue_process:

            group_id = 1
            group_ids = Task.objects.filter(
                group__contains="extraction"
            ).values_list("group", flat=True).order_by("-group").distinct("group")

            if group_ids:
                group_ids = [int(g.split("-")[1]) for g in group_ids]
                group_ids.sort(reverse=True)
                group_id = group_ids[0] + group_id
            
            print("="*100)
            print("Info:\n")
            if not user_id:
                print('* Email notification for failed task are not enabled')
            else:
                print(F'* Email notifications for failed tasks will be sent to {user.email}')

            print(F"* Total number for variables to be processed: {variables.count()}")
            print(F"* Id to recheck tasks ran in this instance: {group_id}")
            print("="*100)

            for variable in variables:
                async_task(
                    "wazimap_ng.datasets.tasks.indicator_data_extraction",
                    variable,
                    task_name=f"Migration Data Extraction: {variable.id} {variable.name}",
                    hook="wazimap_ng.datasets.hooks.process_task_info",
                    group=F"extraction-{group_id}",
                    type="data_extraction", assign=False, notify=False, user_id=user_id,
                    email_on_fail=True if user_id else False
                )

            
                        

