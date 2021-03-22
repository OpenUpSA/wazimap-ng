from typing import Callable, OrderedDict

from django.contrib import messages
from django.contrib.admin.options import ModelAdmin
from django.contrib.gis import admin
from django.contrib.gis.db.models import PointField
from django.contrib.postgres import fields
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django_json_widget.widgets import JSONEditorWidget
from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field
from mapwidgets.widgets import GooglePointFieldWidget

from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.points.models import Category, Location


def assign_to_category_action(category: Category) -> Callable:
    def assign_to_category(modeladmin: ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(category=category)
        messages.info(request, "Locations assigned to category {0}".format(category.name))

    assign_to_category.short_description = "Assign to {0}".format(category.name)
    assign_to_category.__name__ = 'assign_to_category_{0}'.format(category.id)

    return assign_to_category


class LocationResource(resources.ModelResource):
    latitude = Field()
    longitude = Field()
    category = Field()

    def dehydrate_latitude(self, location: Location) -> float:
        return location.coordinates.y

    def dehydrate_longitude(self, location: Location) -> float:
        return location.coordinates.x

    def dehydrate_category(self, location: Location) -> Category:
        return location.category.name

    class Meta:
        model = Location
        fields = ("name", "category", "latitude", "longitude", "data",)
        export_order = ("name", "category", "latitude", "longitude", "data")


@admin.register(Location)
class LocationAdmin(ExportMixin, BaseAdminModel):
    formfield_overrides = {
        fields.JSONField: {"widget": JSONEditorWidget},
        PointField: {"widget": GooglePointFieldWidget},
    }

    list_display = ("name", "category",)
    list_filter = ("category__profile", filters.CollectionFilter,)
    search_fields = ("name",)
    resource_class = LocationResource

    def get_actions(self, request: HttpRequest) -> OrderedDict:
        actions = super().get_actions(request)

        for category in Category.objects.all():
            action = assign_to_category_action(category)
            actions[action.__name__] = (
                action, action.__name__, action.short_description
            )

        return actions
