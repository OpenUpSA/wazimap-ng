from django.contrib import admin

from ..services import permissions

from wazimap_ng.profile.models import Profile
from wazimap_ng.points.models import Category
from wazimap_ng.datasets.models import GeographyHierarchy, Dataset, MetaData as DatasetMetaData, Indicator


class DynamicBaseFilter(admin.SimpleListFilter):
    title = None
    parameter_name = None
    model_class= None
    lookup_fields = ["id", "name"]

    def lookups(self, request, model_admin):
        choices = getattr(
            permissions, "get_custom_fk_queryset"
        )(request.user, self.model_class)

        return choices.values_list(*self.lookup_fields)

    def queryset(self, request, queryset):
        value = self.value()
        if value is None:
            return queryset
        return queryset.filter(**{
            self.parameter_name: value
        })


# Profile Filter
class ProfileFilter(DynamicBaseFilter):
    title = 'Profile'
    parameter_name = 'profile_id'
    model_class = Profile

class ProfileNameFilter(ProfileFilter):
    parameter_name = 'profile__name'
    lookup_fields = ["profile__name", "profile__name"]


# Datasets App Filters
class GeographyHierarchyFilter(DynamicBaseFilter):
    title = 'Geography Hierarchy'
    parameter_name = 'geography_hierarchy_id'
    model_class = GeographyHierarchy


class DatasetFilter(DynamicBaseFilter):
    title = 'Dataset'
    parameter_name = 'dataset_id'
    model_class = Dataset


class DatasetMetaDataFilter(DynamicBaseFilter):
    title = 'Source'
    parameter_name = 'metadata__source'
    model_class = Dataset
    lookup_fields = ["metadata__source", "metadata__source"]


class IndicatorFilter(DynamicBaseFilter):
    title = 'Variable'
    parameter_name = 'indicator__id'
    model_class = Indicator