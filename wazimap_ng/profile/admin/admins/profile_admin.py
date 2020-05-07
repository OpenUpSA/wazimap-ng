import json

from django.contrib.gis import admin
from django.contrib.auth.models import Group

from ... import models

from guardian.shortcuts import get_perms_for_model, assign_perm, remove_perm
from wazimap_ng.general.services import permissions

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        return permissions.get_objects_for_user(request.user, "view", models.Profile, qs)

    def has_change_permission(self, request, obj=None):
    	if not obj:
    		return super().has_change_permission(request, obj)

    	if obj.permission_type == "public":
    		return True
    	return request.user.has_perm("change_profile", obj)

    def has_delete_permission(self, request, obj=None):
    	if not obj:
    		return super().has_delete_permission(request, obj)
    	return request.user.has_perm("delete_profile", obj)


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            for perm in get_perms_for_model(models.Profile):
                assign_perm(perm, request.user, obj)
        return obj