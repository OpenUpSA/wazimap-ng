import json

from django.contrib.gis import admin
from django.contrib.auth.models import Group

from ... import models

from guardian.shortcuts import get_perms_for_model, assign_perm, remove_perm
from wazimap_ng.general.admin.admin_base import BaseAdminModel

@admin.register(models.Profile)
class ProfileAdmin(BaseAdminModel):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change or (change and obj.permission_type == "private"):
            group, created = Group.objects.get_or_create(name=obj.name.lower())
            for perm in get_perms_for_model(models.Profile):
                assign_perm(perm, group, obj)
        return obj