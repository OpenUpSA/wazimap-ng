from django.contrib.gis import admin

from ... import models
from wazimap_ng.general.services import permissions

@admin.register(models.Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ("profile",)
    list_filter = ("profile",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "profile":
            kwargs["queryset"] = permissions.get_objects_for_user(request.user, "view", models.Profile)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        profiles = permissions.get_objects_for_user(request.user, "view", models.Profile)
        return qs.filter(profile__in=profiles)