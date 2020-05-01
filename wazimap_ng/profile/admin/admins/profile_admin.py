import json

from django.contrib.gis import admin
from django.contrib.auth.models import Group

from ... import models
from ..forms import ProfileAdminForm

from guardian.shortcuts import get_perms_for_model, assign_perm, remove_perm
from wazimap_ng.general.services import permissions

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm

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
        
        permissions_added = json.loads(request.POST.get("permissions_added", "{}"))
        permissions_removed = json.loads(request.POST.get("permissions_removed", "{}"))

        for group_id, perms in permissions_removed.items():
            group = Group.objects.filter(id=group_id).first()
            if group:
                for perm in perms:
                    remove_perm(perm, group, obj)

        for group_id, perms in permissions_added.items():
            group = Group.objects.filter(id=group_id).first()
            if group:
                for perm in perms:
                    assign_perm(perm, group, obj)
        
        if not change:
            for perm in get_perms_for_model(models.Profile):
                assign_perm(perm, request.user, obj)
        return obj

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.target = obj
        return form