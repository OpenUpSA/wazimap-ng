from django.contrib.gis import admin
from adminsortable2.admin import SortableAdminMixin

from ... import models
from ..forms import ProfileHighlightForm

from wazimap_ng.admin_utils import customTitledFilter, description
from wazimap_ng.datasets.models import Indicator, Dataset
from wazimap_ng.utils import get_objects_for_user

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
            kwargs["queryset"] = get_objects_for_user(request.user, "view", models.Profile)

        if db_field.name == "indicator":
            profiles = get_objects_for_user(request.user, "view", models.Profile)
            herarchies = profiles.values_list("geography_hierarchy")
            datasets = get_objects_for_user(request.user, "view", Dataset)
            kwargs["queryset"] = Indicator.objects.filter(
                dataset__in=datasets.filter(geography_hierarchy__in=herarchies)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        profiles = get_objects_for_user(request.user, "view", models.Profile)
        return qs.filter(profile__in=profiles)