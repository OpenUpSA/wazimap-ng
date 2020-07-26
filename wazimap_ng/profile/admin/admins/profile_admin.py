from django.contrib.gis import admin
from django.contrib.postgres import fields

from django_json_widget.widgets import JSONEditorWidget

from ... import models

from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.services.permissions import assign_perms_to_group
from wazimap_ng.general.admin import filters

@admin.register(models.Profile)
class ProfileAdmin(BaseAdminModel):

    list_display = ('name', 'geography_hierarchy',)
    list_filter = (filters.GeographyHierarchyFilter,)
    formfield_overrides = {
        fields.JSONField: {"widget": JSONEditorWidget},
    }

    def save_model(self, request, obj, form, change):
        is_new = obj.pk == None and change == False
        super().save_model(request, obj, form, change)
        if is_new:
            assign_perms_to_group(obj.name, obj)
        return obj

    class Media:
        js = ("/static/js/geography_hierarchy.js",)