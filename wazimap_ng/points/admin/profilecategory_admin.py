from typing import Sequence

from adminsortable2.admin import SortableAdminMixin
from django.contrib.gis import admin
from django.forms import Form, ModelForm
from django.http.request import HttpRequest
from icon_picker_widget.widgets import IconPickerWidget

from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.services.permissions import assign_perms_to_group
from wazimap_ng.points.models import ProfileCategory, Theme


class ProfileCategoryAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = IconPickerWidget()


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

@admin.register(ProfileCategory)
class ProfileCategoryAdmin(SortableAdminMixin, BaseAdminModel):
    list_display = ("label", "theme", "order", "category", "profile")
    list_filter = (filters.ProfileFilter, filters.ThemeFilter, filters.CollectionFilter)

    fieldsets = (
        ("Database fields (can't change after being created)", {
            'fields': ('profile', 'theme', 'category',)
        }),
        ("Profile Collection Icon & Color", {
            'fields': ('icon', 'color', )

        }),
        ("Point Collection description fields", {
            'fields': ('label', 'description',)
        }),
        ("Point Collection configuration", {
            'fields': ('visible_tooltip_attributes',)
        }),
    )
    form = ProfileCategoryAdminForm
    search_fields = ("label", )

    class Media:
        css = {
            'all': ('/static/css/admin-custom.css',)
        }
        js = (
            "/static/js/profile_theme.js",
        )

    def get_readonly_fields(self, request: HttpRequest, obj: ProfileCategory = None) -> Sequence:
        if obj:
            return ("profile", "category", ) + self.readonly_fields
        return self.readonly_fields

    def save_model(self, request: HttpRequest, obj: ProfileCategory, form: ProfileCategoryAdminForm, change: bool) -> ProfileCategory:
        is_new = obj.pk == None and change == False
        is_profile_updated = change and "profile" in form.changed_data

        super().save_model(request, obj, form, change)
        if is_new or is_profile_updated:
            assign_perms_to_group(obj.profile.name, obj, is_profile_updated)
        return obj

    def get_form(self, request: HttpRequest, obj: ProfileCategory=None, **kwargs) -> Form:
        schema = DEFAULT_SCHEMA
        if obj:
            schema = dynamic_schema(obj)
        widget = JSONEditorWidget(schema, False)
        form = super().get_form(request, obj, widgets={'attributes': widget}, **kwargs)

        qs = form.base_fields["theme"].queryset
        if obj:
            qs = Theme.objects.filter(profile_id=obj.profile_id)
        elif not obj and request.method == "GET":
            qs = qs = Theme.objects.none()

        form.base_fields["theme"].queryset = qs

        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "category":
            field.queryset = field.queryset.order_by("name")
        return field
