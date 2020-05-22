from django.contrib.gis import admin
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.services.permissions import assign_perms_to_group

from .. import models
from .forms import CategoryAdminForm


@admin.register(models.Category)
class CategoryAdmin(BaseAdminModel):
    list_display = ("name", "theme",)
    list_filter = ("theme",)
    form = CategoryAdminForm
    exclude = ("metadata", )

    fieldsets = (
        ("", {
            'fields': ('profile', 'theme', 'name', )
        }),
        ("Permissions", {
            'fields': ('permission_type', )

        }),
        ("MetaData", {
          'fields': ('source', 'description', 'licence', )
        }),
    )

    class Media:
        css = {
             'all': ('/static/css/admin-custom.css',)
        }

    def save_model(self, request, obj, form, change):
        is_new = obj.pk == None and change == False
        super().save_model(request, obj, form, change)
        if is_new or obj.permission_type == "private":
            assign_perms_to_group(obj.profile.name, obj)
        return obj
