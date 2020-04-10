from django.db import models

from django.contrib.postgres.fields import JSONField, ArrayField

from .dataset import Indicator, DatasetData, Universe, CountryDataExtractor
from .geography import Geography, GeographyHierarchy

class Profile(models.Model):
    name = models.CharField(max_length=50)
    indicators = models.ManyToManyField(Indicator, through="ProfileIndicator", verbose_name="variables")
    geography_hierarchy = models.ForeignKey(GeographyHierarchy, on_delete=models.PROTECT, null=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class IndicatorCategory(models.Model):
    name = models.CharField(max_length=25)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.profile.name} -> {self.name}"

    class Meta:
        verbose_name_plural = "Indicator Categories"
        ordering = ["id"]


class IndicatorSubcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(IndicatorCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.category.name} -> {self.name}"

    class Meta:
        verbose_name_plural = "Indicator Subcategories"
        ordering = ["id"]


class ProfileIndicator(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, help_text="Indicator on which this indicator is based on.", verbose_name="variable")
    subcategory = models.ForeignKey(IndicatorSubcategory, on_delete=models.CASCADE)
    label = models.CharField(max_length=60, null=False, blank=True, help_text="Label for the indicator displayed on the front-end")
    description = models.TextField(blank=True)
    subindicators = JSONField(default=list, blank=True)
    choropleth_method = models.ForeignKey("profile.ChoroplethMethod", null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.profile.name} -> {self.label}"

    class Meta:
        ordering = ["id"]

class ProfileHighlight(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, help_text="Indicator on which this highlight is based on.", verbose_name="variable")
    name = models.CharField(max_length=60, null=False, blank=True, help_text="Name of the indicator in the database")
    label = models.CharField(max_length=60, null=False, blank=True, help_text="Label for the indicator displayed on the front-end")
    subindicator = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Highlight: {self.label}"

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

    def refresh_profiles(self, profile, data_extractor):
        self.clear_profiles(profile)
        self.add_all_indicators(profile, data_extractor)
        self.add_highlights(profile, data_extractor)

    def add_highlights(self, profile, data_extractor):
        print("== Adding highlights ==")
        for highlight in ProfileHighlight.objects.filter(profile=profile):
            print(f"Loading {highlight.indicator.name}")
            self.add_indicator(profile, highlight, data_extractor, "highlights")

    def add_all_indicators(self, profile, data_extractor):
        print("== Adding indicators ==")
        for profile_indicator in ProfileIndicator.objects.filter(profile=profile):
            print(f"Loading {profile_indicator.indicator.label}")
            self.add_indicator(profile, profile_indicator, data_extractor, "indicators")

    def add_indicator(self, profile, profile_indicator, data_extractor, namespace=None):
        universe = profile_indicator.indicator.universe
        indicator = profile_indicator.indicator

        counts = data_extractor.get_queryset(indicator, self.values("geography"), universe=universe)

        profile_code = None
        obj = None
        indicator_data = None

        objs = []
        profiles = self.load_profiles(profile)

        for count in counts:
            new_code = count["geography"]
            del count["geography"]

            if profile_code != new_code:
                profile_code = new_code

                if obj is not None:
                    indicator_data[profile_indicator.name] = indicator_value
                    #obj.data[profile_indicator.name] = indicator_value
                    objs.append(obj)

                obj = profiles[new_code]
                indicator_data = obj.data.setdefault(namespace, {})

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
            indicator_data[profile_indicator.name] = indicator_value
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

    def rollup_country(self, profile):
        """
        Country data is generally not available in uploaded querysets and needs to be aggregated from lower-level data
        """
        country = Geography.objects.filter(level='country').first()
        extractor = CountryDataExtractor(country)
        self.get_queryset().add_all_indicators(profile, extractor)


class ProfileData(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    data = JSONField()

    objects = ProfileDataManager()
    
    class Meta:
        ordering = ["id"]

