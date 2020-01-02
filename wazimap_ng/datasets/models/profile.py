from django.db import models

from django.contrib.postgres.fields import JSONField

from .dataset import Indicator, DatasetData, Universe, DataExtractor
from .geography import Geography

class Profile(models.Model):
    name = models.CharField(max_length=50)
    indicators = models.ManyToManyField(Indicator, through="ProfileIndicator")

    def __str__(self):
        return self.name

class IndicatorCategory(models.Model):
    name = models.CharField(max_length=25)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.profile.name} -> {self.name}"

    class Meta:
        verbose_name_plural = "Indicator Categories"

class IndicatorSubcategory(models.Model):
    name = models.CharField(max_length=25)
    category = models.ForeignKey(IndicatorCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.category.name} -> {self.name}"

    class Meta:
        verbose_name_plural = "Indicator Subcategories"


class ProfileIndicator(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, help_text="Indicator on which this indicator is based on.")
    subcategory = models.ForeignKey(IndicatorSubcategory, on_delete=models.CASCADE)
    key_metric = models.BooleanField(default=False, help_text="Used as a headline metric in the profile.")
    universe = models.ForeignKey(Universe, null=True, blank=True, on_delete=models.CASCADE, help_text="The subset of the population considered for this indicator.")
    name = models.CharField(max_length=60, null=False, blank=True, help_text="Name of the indicator in the database")
    label = models.CharField(max_length=60, null=False, blank=True, help_text="Label for the indicator displayed on the front-end")

    def __str__(self):
        return f"{self.profile.name} -> {self.label}"

class ProfileDataQuerySet(models.QuerySet):

    def load_profiles(self, profile):
        return {
            profile_datum.geography.pk: profile_datum
            for profile_datum in (
                self 
                    .filter(profile=profile)
                    .select_related("geography")
            )
        }

    def clear_profiles(self, profile):
        profiles = self.load_profiles(profile).values()
        for profile in profiles:
            profile.data = {}

        self.bulk_update(profiles, ["data"], batch_size=1000)

    def add_all_indicators(self, profile):
        for profile_indicator in profile.profileindicator_set.all():
            print(f"Loading {profile_indicator.indicator.name}")
            self.add_indicator(profile, profile_indicator)

    def add_indicator(self, profile, profile_indicator):
        universe = profile_indicator.universe
        indicator = profile_indicator.indicator

        data_extractor = DataExtractor(indicator, self.values("geography"), universe=universe)

        counts = data_extractor.get_queryset()
        print(counts.query)

        profile_code = None
        obj = None

        objs = []
        profiles = self.load_profiles(profile)

        for count in counts:
            print(count)
            new_code = count["geography"]
            del count["geography"]

            if profile_code != new_code:
                profile_code = new_code

                if obj is not None:
                    obj.data[profile_indicator.name] = indicator_value
                    objs.append(obj)

                obj = profiles[new_code]

                indicator_value = []

            # Not supporting multiple variables to disaggregate on temporarily
            #value = {g: count["data__" + g] for g in indicator.groups}
            value = {"key": count["data__" + g] for g in indicator.groups}

            is_singleton = len(value) == 0
            if is_singleton:
                value = {"key": "Total"}

            value["count"] = count["count"]
            indicator_value.append(value)

        if obj is not None:
            obj.data[profile_indicator.name] = indicator_value
            objs.append(obj)

        self.bulk_update(objs, ["data"], batch_size=1000)


class ProfileDataManager(models.Manager):
    def get_queryset(self):
        return ProfileDataQuerySet(self.model, using=self._db)

    def create_profiles(self, profile, batch_size=1000):
        data_profiles = ProfileData.objects.filter(profile=profile).select_related("geography")
        codes = set(data_profile.geography.code for data_profile in data_profiles)

        objs = [
            ProfileData(profile=profile, geography=geography, data={})
            for geography in Geography.objects.all()
            if geography.code not in codes
        ]

        ProfileData.objects.bulk_create(objs, batch_size=batch_size)

    def load_profiles(self, profile):
        return self.get_queryset().load_profiles(profile)

    def add_indicator(self, profile, indicator):
        return self.get_queryset().add_indicator(profile, indicator)

class ProfileData(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    data = JSONField()

    objects = ProfileDataManager()

