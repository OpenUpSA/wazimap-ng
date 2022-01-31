from django.contrib.gis import admin
from django.contrib.postgres import fields
from django.db.models.functions import Lower
from django_json_widget.widgets import JSONEditorWidget

from ... import models

from wazimap_ng.general.admin.admin_base import BaseAdminModel, HistoryAdmin
from wazimap_ng.general.admin.forms import HistoryAdminForm
from wazimap_ng.general.services.permissions import assign_perms_to_group
from wazimap_ng.general.admin import filters


@admin.register(models.Profile)
class ProfileAdmin(BaseAdminModel, HistoryAdmin):

    list_display = (
        "name",
        "geography_hierarchy",
    )
    list_filter = (filters.GeographyHierarchyFilter,)
    formfield_overrides = {
        fields.JSONField: {"widget": JSONEditorWidget},
    }
    fieldsets = (
        ("", {
            "fields": (
                "name", "geography_hierarchy", "permission_type",
                "description", "configuration"
            )
        }),
    )

    form = HistoryAdminForm

    def get_ordering(self, request):
        return [Lower("name")]

    def save_model(self, request, obj, form, change):
        is_new = obj.pk == None and change == False
        super().save_model(request, obj, form, change)
        if is_new:
            assign_perms_to_group(obj.name, obj)
        return obj

    class Media:
        js = ("/static/js/geography_hierarchy.js",)
