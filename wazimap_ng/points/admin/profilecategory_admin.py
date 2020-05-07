import json

from django.contrib.gis import admin
from django.contrib.auth.models import Group
from django import forms

from guardian.shortcuts import get_perms_for_model, assign_perm, remove_perm

from wazimap_ng.profile.models import Profile
from wazimap_ng.general.services import permissions
from wazimap_ng.admin_utils import GroupPermissionWidget

from .. import models

class PointsCollectionAdminForm(forms.ModelForm):
    group_permissions = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, widget=GroupPermissionWidget)
    class Meta:
        model = models.ProfileCategory
        widgets = {
          'permission_type': forms.RadioSelect,
        }
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group_permissions"].widget.init_parameters(self.current_user, self.instance, self.instance.permission_type)


@admin.register(models.ProfileCategory)
class ProfileCategoryAdmin(admin.ModelAdmin):
    list_display = ("label", "category", "profile")
    list_filter = ("category", "profile",)
    form = PointsCollectionAdminForm

    fieldsets = (
        ("Database fields (can't change after being created)", {
            'fields': ('profile', 'category',)
        }),
        ("Permissions", {
            'fields': ('permission_type', 'group_permissions', )

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

        if is_new:
            for perm in get_perms_for_model(models.ProfileCategory):
                assign_perm(perm, request.user, obj)
        return obj

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        profile_ids = permissions.get_objects_for_user(
            request.user, 'view', Profile
        ).values_list("id", flat=True)

        qs = permissions.get_objects_for_user(request.user, 'view', models.ProfileCategory, qs)
        return qs.filter(profile_id__in=profile_ids)

    def has_change_permission(self, request, obj=None):
        if not obj:
            return super().has_change_permission(request, obj)

        if obj.permission_type == "public":
            return True
        return request.user.has_perm("change_profilecategory", obj)

    def has_delete_permission(self, request, obj=None):
        if not obj:
            return super().has_delete_permission(request, obj)
        return request.user.has_perm("delete_profilecategory", obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.target = obj
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "profile":
            kwargs["queryset"] = permissions.get_objects_for_user(request.user, "view", Profile)

        if db_field.name == "category":
            kwargs["queryset"] = permissions.get_objects_for_user(request.user, "view", models.Category)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)