from django.db import models

from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields.jsonb import KeyTextTransform, KeyTransform
from django.db.models.functions import Cast
from django.db.models import Sum

from .dataset import Indicator, DatasetData
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
        return self.name

    class Meta:
        verbose_name_plural = "Indicator Subcategories"


class ProfileIndicator(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(IndicatorSubcategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.profile.name} -> {self.indicator.name}"

class ProfileDataManager(models.Manager):
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
        return {
            profile_datum.geography.pk: profile_datum
            for profile_datum in (
                ProfileData.objects
                    .filter(profile=profile)
                    .select_related("geography")
            )
        }

    def add_indicator(self, profile, indicator):

        groups = ["data__" + i for i in indicator.groups] + ["geography"]
        c = Cast(KeyTextTransform("Count", "data"), models.IntegerField())
        counts = (
            DatasetData.objects
                .filter(dataset=indicator.dataset)
                .values(*groups)
                .annotate(count=Sum(c))
                .order_by("geography")
        )
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
                    obj.data[indicator.name] = indicator_value
                    objs.append(obj)

                obj = profiles[new_code]

                indicator_value = []

            # Not supporting multiple variables to disaggregate on temporarily
            #value = {g: count["data__" + g] for g in indicator.groups}
            value = {"key": count["data__" + g] for g in indicator.groups}
            value["count"] = count["count"]
            indicator_value.append(value)

        if obj is not None:
            obj.data[indicator.name] = indicator_value
            objs.append(obj)

        self.bulk_update(objs, ["data"], batch_size=1000)

class ProfileData(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    data = JSONField()

    objects = ProfileDataManager()

