from django.contrib.gis import admin
from django.contrib.auth.models import Group
from wazimap_ng.general.admin.admin_base import BaseAdminModel

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

        if is_new or (change and obj.permission_type == "private"):
            group = Group.objects.filter(name=obj.theme.profile.name.lower()).first()
            for perm in get_perms_for_model(models.Category):
                assign_perm(perm, group, obj)
        return obj
