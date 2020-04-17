from django.contrib.gis import admin
from adminsortable2.admin import SortableAdminMixin

from ... import models
from ..forms import ProfileHighlightForm
from guardian.shortcuts import get_objects_for_user


from wazimap_ng.admin_utils import customTitledFilter, description

@admin.register(models.ProfileHighlight)
class ProfileHighlightAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_filter = (
        ("profile__name", customTitledFilter("Profile")),
    )

    list_display = (
        "profile", 
        "name", 
        "label", 
        description("Indicator", lambda x: x.indicator.name), 
        "order", 
    )

    fieldsets = (
        ("Database fields (can't change after being created)", {
            "fields": ("profile", "name", "indicator")
        }),
        ("Profile fields", {
          "fields": ("label", "subindicator", "denominator")
        })
    )
    form = ProfileHighlightForm

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile", "name") + self.readonly_fields
        return self.readonly_fields

    class Media:
        js = (
            "/static/js/jquery-ui.min.js",
            "/static/js/variable_subindicators.js",
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "profile":
            profiles = models.Profile.objects.all().exclude(profile_type="private")
            profiles |= get_objects_for_user(request.user, 'profile.view_profile', accept_global_perms=False)
            kwargs["queryset"] = profiles
        return super().formfield_for_foreignkey(db_field, request, **kwargs)