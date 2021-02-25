from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.services.permissions import assign_perms_to_group

from . import models


@admin.register(models.Page)
class PageAdmin(BaseAdminModel):
    list_display = ("name", 'profile', 'api_mapping',)

    def save_model(self, request, obj, form, change):
        is_new = obj.pk == None and change == False
        is_profile_updated = change and "profile" in form.changed_data
        super().save_model(request, obj, form, change)

        if is_new or is_profile_updated:
            assign_perms_to_group(obj.profile.name, obj, is_profile_updated)
        return obj


@admin.register(models.Content)
class ContentAdmin(SortableAdminMixin, BaseAdminModel):
    list_filter = [filters.PageFilter]
    list_display = ("title", 'page', 'order',)

    def save_model(self, request, obj, form, change):
        is_new = obj.pk == None and change == False
        super().save_model(request, obj, form, change)

        if is_new or is_profile_updated:
            assign_perms_to_group(obj.page.profile.name, obj)
        return obj
