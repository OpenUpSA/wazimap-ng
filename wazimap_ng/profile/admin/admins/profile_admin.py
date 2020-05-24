from django.contrib.gis import admin

from ... import models

from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.services.permissions import assign_perms_to_group

@admin.register(models.Profile)
class ProfileAdmin(BaseAdminModel):

    def save_model(self, request, obj, form, change):
        is_new = obj.pk == None and change == False
        super().save_model(request, obj, form, change)
        if is_new or obj.permission_type == "private":
            assign_perms_to_group(obj.name, obj)
        return obj