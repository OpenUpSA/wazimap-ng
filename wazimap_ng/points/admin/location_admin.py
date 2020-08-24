from django.contrib.postgres import fields
from django.contrib.gis import admin
from django.contrib.gis.db.models import PointField
from django.contrib import messages

from import_export.admin import ExportMixin
from import_export import resources
from import_export.fields import Field

from django_json_widget.widgets import JSONEditorWidget
from mapwidgets.widgets import GooglePointFieldWidget
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.admin import filters

from .. import models

def assign_to_category_action(category):
    def assign_to_category(modeladmin, request, queryset):
        queryset.update(category=category)
        messages.info(request, "Locations assigned to category {0}".format(category.name))

    assign_to_category.short_description = "Assign to {0}".format(category.name)
    assign_to_category.__name__ = 'assign_to_category_{0}'.format(category.id)

    return assign_to_category


class LocationResource(resources.ModelResource):
    latitude = Field()
    longitude = Field()
    category = Field()

    def dehydrate_latitude(self, location):
        return location.coordinates.y

    def dehydrate_longitude(self, location):
        return location.coordinates.x

    def dehydrate_category(self, location):
        return location.category.name

    class Meta:
        model = models.Location
        fields = ("name", "category", "latitude", "longitude", "data",)
        export_order = ("name", "category", "latitude", "longitude", "data")



@admin.register(models.Location)
class LocationAdmin(ExportMixin, BaseAdminModel):
    formfield_overrides = {
        fields.JSONField: {"widget": JSONEditorWidget},
        PointField: {"widget": GooglePointFieldWidget},
    }

    list_display = ("name", "category",)
    list_filter = ("category__profile", filters.CollectionFilter,)
    search_fields = ("name",)
    resource_class = LocationResource

    def get_actions(self, request):
        actions = super().get_actions(request)

        for category in models.Category.objects.all():
            action = assign_to_category_action(category)
            actions[action.__name__] = (
                action, action.__name__, action.short_description
            )

        return actions
