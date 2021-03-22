from typing import List

from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from wazimap_ng.cms.models import Page
from wazimap_ng.datasets.models import Dataset, GeographyHierarchy, Indicator
from wazimap_ng.points.models import Category, Theme
from wazimap_ng.profile.models import (
    IndicatorCategory,
    IndicatorSubcategory,
    Profile
)

from ..services import permissions


class DynamicBaseFilter(admin.SimpleListFilter):
    title = None
    parameter_name = None
    model_class = None
    lookup_fields = ["id", "name"]

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> List:
        choices = getattr(
            permissions, "get_custom_queryset"
        )(self.model_class, request.user)
        return list(set(choices.values_list(*self.lookup_fields)))

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        value = self.value()
        if value is None:
            return queryset
        return queryset.filter(**{
            self.parameter_name: value
        }).distinct()


# Profile Filter
class ProfileFilter(DynamicBaseFilter):
    title = 'Profile'
    parameter_name = 'profile_id'
    model_class = Profile


class ProfileNameFilter(ProfileFilter):
    parameter_name = 'profile__name'
    lookup_fields = ["name", "name"]


class CategoryFilter(DynamicBaseFilter):
    title = "Category"
    parameter_name = 'category_id'
    model_class = IndicatorCategory

    def lookups(self, request, model_admin):
        choices = getattr(
            permissions, "get_custom_queryset"
        )(self.model_class, request.user)
        return [(category.id, category) for category in choices]


class SubCategoryFilter(DynamicBaseFilter):
    title = "Subcategory"
    parameter_name = 'subcategory_id'
    model_class = IndicatorSubcategory


class ThemeFilter(DynamicBaseFilter):
    title = "Theme"
    parameter_name = 'theme_id'
    model_class = Theme

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> List:
        profiles = permissions.get_objects_for_user(
            request.user, Profile, include_public=True
        )
        return [(theme.id, theme) for theme in self.model_class.objects.filter(
            profile__in=profiles
        )]


# Datasets App Filters
class GeographyHierarchyFilter(DynamicBaseFilter):
    title = 'Geography Hierarchy'
    parameter_name = 'geography_hierarchy_id'
    model_class = GeographyHierarchy

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> List:
        choices = getattr(
            permissions, "get_custom_fk_queryset"
        )(request.user, self.model_class)
        return list(set(choices.values_list(*self.lookup_fields)))


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


class CollectionFilter(DynamicBaseFilter):
    title = 'Collection'
    parameter_name = 'category_id'
    model_class = Category

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> List:
        choices = getattr(
            permissions, "get_custom_queryset"
        )(self.model_class, request.user)
        return [(collection.id, collection) for collection in choices]

# CMS


class PageFilter(DynamicBaseFilter):
    title = 'Page'
    parameter_name = 'page_id'
    model_class = Page

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> List:
        choices = getattr(
            permissions, "get_custom_fk_queryset"
        )(request.user, self.model_class)
        return list(set(choices.values_list(*self.lookup_fields)))
