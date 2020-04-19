from django.contrib.gis import admin

from ... import models
from ..forms import ProfileHighlightForm


from wazimap_ng.admin_utils import customTitledFilter, description

@admin.register(models.ProfileHighlight)
class ProfileHighlightAdmin(admin.ModelAdmin):
    list_filter = (
        ("profile__name", customTitledFilter("Profile")),
        ("indicator__name", customTitledFilter("Indicator")),
    )

    list_display = (
        "profile", 
        "name", 
        "label", 
        description("Indicator", lambda x: x.indicator.name), 
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