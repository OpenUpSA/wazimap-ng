from django.contrib.gis import admin

from wazimap_ng.general.services import permissions
from wazimap_ng.profile.models import Profile

from .. import models


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "profile",)
    list_filter = ("profile",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "profile":
            kwargs["queryset"] = permissions.get_objects_for_user(request.user, "view", Profile)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        profile_ids = permissions.get_objects_for_user(
            request.user, 'view', Profile
        ).values_list("id", flat=True)

        return qs.filter(profile_id__in=profile_ids)