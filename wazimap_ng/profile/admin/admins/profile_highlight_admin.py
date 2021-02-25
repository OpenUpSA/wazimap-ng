from adminsortable2.admin import SortableAdminMixin
from django.contrib.gis import admin

from wazimap_ng.datasets.models import Dataset, Indicator
from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.services import permissions
from wazimap_ng.general.widgets import customTitledFilter, description

from ... import models
from ..forms import ProfileHighlightForm


@admin.register(models.ProfileHighlight)
class ProfileHighlightAdmin(SortableAdminMixin, BaseAdminModel):

    list_filter = (filters.ProfileNameFilter, )

    exclude_common_list_display = True
    list_display = (
        "profile",
        "label",
        description("Indicator", lambda x: x.indicator.name),
        "created",
        "updated",
        "order",
    )

    fieldsets = (
        ("Database fields (can't change after being created)", {
            "fields": ("profile", "indicator")
        }),
        ("Profile fields", {
          "fields": ("label", "subindicator", "denominator")
        })
    )
    form = ProfileHighlightForm
    search_fields = ("label", )

    help_texts = ["denominator", ]

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile",) + self.readonly_fields
        return self.readonly_fields

    class Media:
        js = (
            "/static/js/variable_subindicators.js",
        )
