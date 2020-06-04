from django.contrib.gis import admin

from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.services.permissions import assign_perms_to_group

from .. import models


@admin.register(models.ProfileCategory)
class ProfileCategoryAdmin(BaseAdminModel):
    list_display = ("label", "category", "profile")
    list_filter = ("category", "profile",)

    fieldsets = (
        ("Database fields (can't change after being created)", {
            'fields': ('profile', 'category',)
        }),
        ("Permissions", {
            'fields': ('permission_type', )

        }),
        ("Point Collection description fields", {
          'fields': ('label', 'description',)
        }),
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