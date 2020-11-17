from adminsortable2.admin import SortableAdminMixin
from django.contrib.gis import admin
from django import forms

from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.services.permissions import assign_perms_to_group
from wazimap_ng.general.admin import filters

from .. import models

from icon_picker_widget.widgets import IconPickerWidget


class ProfileCategoryAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = IconPickerWidget()


@admin.register(models.ProfileCategory)
class ProfileCategoryAdmin(SortableAdminMixin, BaseAdminModel):
    list_display = ("label", "theme", "order", "category", "profile")
    list_filter = (filters.ProfileFilter, filters.ThemeFilter, filters.CollectionFilter)

    fieldsets = (
        ("Database fields (can't change after being created)", {
            'fields': ('profile', 'theme', 'category',)
        }),
        ("Profile Collection Icon", {
            'fields': ('icon', )

        }),
        ("Point Collection description fields", {
          'fields': ('label', 'description',)
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
        form = super().get_form(request, obj, **kwargs)

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
