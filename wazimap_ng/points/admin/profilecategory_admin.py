import json

from django.contrib.gis import admin
from django.contrib.auth.models import Group
from django import forms

from guardian.shortcuts import get_perms_for_model, assign_perm, remove_perm

from wazimap_ng.profile.models import Profile
from wazimap_ng.general.admin.admin_base import BaseAdminModel

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
        if obj: # editing an existing object
            return ("profile", "category", ) + self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        is_new = obj.pk == None and change == False
        super().save_model(request, obj, form, change)

        if is_new or (change and obj.permission_type == "private"):
            group = Group.objects.filter(name=profile.name.lower()).first()
            for perm in get_perms_for_model(models.ProfileCategory):
                assign_perm(perm, group, obj)
        return obj