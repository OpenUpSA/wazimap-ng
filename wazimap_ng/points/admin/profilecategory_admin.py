from adminsortable2.admin import SortableAdminMixin
from django.contrib.gis import admin
from django import forms
from django.contrib.postgres import fields

from django_json_widget.widgets import JSONEditorWidget

from wazimap_ng.general.admin.admin_base import BaseAdminModel, HistoryAdmin
from wazimap_ng.general.admin.forms import HistoryAdminForm
from wazimap_ng.general.services.permissions import assign_perms_to_group
from wazimap_ng.general.admin import filters

from .. import models

class ProfileCategoryAdminForm(HistoryAdminForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


DEFAULT_SCHEMA = {
    'type': 'array',
    'title': 'tags',
    'items': {
        'type': 'string',
        'enum': []
    }
}
def dynamic_schema(obj):
    schema = DEFAULT_SCHEMA
    schema['items']['enum'] = obj.location_attributes
    return schema

@admin.register(models.ProfileCategory)
class ProfileCategoryAdmin(SortableAdminMixin, BaseAdminModel, HistoryAdmin):
    list_display = ("label", "theme", "order", "category", "profile")
    list_filter = (filters.ProfileFilter, filters.ThemeFilter, filters.CollectionFilter)

    fieldsets = (
        ("Database fields (can't change after being created)", {
            'fields': ('profile', 'theme', 'category',)
        }),
        ("Point Collection description fields", {
          'fields': ('label', 'description',)
        }),
        ("Point Collection configuration", {
            'fields': ('visible_tooltip_attributes', 'configuration')
        }),
    )
    form = ProfileCategoryAdminForm
    search_fields = ("label", )
    formfield_overrides = {
        fields.JSONField: {"widget": JSONEditorWidget},
    }

    class Media:
        css = {
             'all': ('/static/css/admin-custom.css',)
        }
        js = (
            "/static/js/profile_theme.js",
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("profile", "category", ) + self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        is_new = obj.pk == None and change == False
        is_profile_updated = change and "profile" in form.changed_data

        super().save_model(request, obj, form, change)
        if is_new or is_profile_updated:
            assign_perms_to_group(obj.profile.name, obj, is_profile_updated)
        return obj

    def get_form(self, request, obj=None, **kwargs):
        schema = DEFAULT_SCHEMA
        if obj:
            schema = dynamic_schema(obj)
        widget = JSONEditorWidget(schema, False)
        form = super().get_form(request, obj, widgets={'attributes': widget}, **kwargs)

        qs = form.base_fields["theme"].queryset
        if obj:
            qs = models.Theme.objects.filter(profile_id=obj.profile_id)
        elif not obj and request.method == "GET":
             qs = qs = models.Theme.objects.none()

        form.base_fields["theme"].queryset = qs

        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "category":
            field.queryset = field.queryset.order_by("name")
        return field
