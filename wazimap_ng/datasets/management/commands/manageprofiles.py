from django.core.management.base import BaseCommand
from django.utils import timezone
from ... import models

class Command(BaseCommand):
    help = "Manage Geography profiles"

    def add_arguments(self, parser):

        parser.add_argument("profile_id", type=int)

        parser.add_argument(
            "--list-profiles",
            action="store_true",
            default=False,
            help="List all profiles. No updates are made."
        )

        parser.add_argument(
            "--list-indicators",
            action="store_true",
            default=False,
            help="List all indicators. No updates are made."
        )

        parser.add_argument(
            "--level",
            action="append",
            help="Geo levels to be updated"
        )

        parser.add_argument(
            "--indicator",
            action="append",
            help="Geo levels to be updated"
        )

    def _get_profile_data(self, levels=None):
        if levels is not None:
            return models.ProfileData.objects.filter(geography__level__in=levels)
        return models.ProfileData.objects.all()

    def handle(self, *args, **options):
        profile = models.Profile.objects.get(pk=options["profile_id"])

        if options["list_profiles"]:
            for profile in models.Profile.objects.all():
                print(f"{profile.id}) {profile.name}")
        elif options["list_indicators"]:
            profile_id = options["profile_id"]
            for indicator in models.ProfileIndicator.objects.filter(profile=profile, profile_id=profile_id):
                print(f"{indicator.id}) {indicator.name}")
        else:
            profile_data = self._get_profile_data(options["level"])
            if options["indicator"]:
                indicators = [int(i) for i in options["indicator"]]
                for pi in models.ProfileIndicator.objects.filter(pk__in=indicators):
                    print(f"Loading {pi.label}")
                    profile_data.add_indicator(profile, pi)
            else:
                print(f"Loading all indicators")
                profile_data.refresh_profiles(profile)
