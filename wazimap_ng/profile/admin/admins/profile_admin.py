from django.contrib.gis import admin

from ... import models
from ..forms import ProfileAdminForm

from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import get_objects_for_user, get_perms_for_model, assign_perm

@admin.register(models.Profile)
class ProfileAdmin(GuardedModelAdmin):
    form = ProfileAdminForm

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile_type", ) + self.readonly_fields
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        profiles = qs.exclude(profile_type="private")
        profiles |= get_objects_for_user(request.user, 'profile.view_profile', accept_global_perms=False)

        return profiles

    def has_change_permission(self, request, obj=None):
    	if not obj:
    		return super().has_change_permission(request, obj)

    	if obj.profile_type == "public":
    		return True
    	return request.user.has_perm("change_profile", obj)

    def has_delete_permission(self, request, obj=None):
    	if not obj:
    		return super().has_delete_permission(request, obj)
    	if obj.profile_type == "public":
    		return True
    	return request.user.has_perm("delete_profile", obj)


    def save_model(self, request, obj, form, change):
    	super().save_model(request, obj, form, change)

    	if not change:
    		for perm in get_perms_for_model(models.Profile):
    			assign_perm(perm, request.user, obj)
    	return obj