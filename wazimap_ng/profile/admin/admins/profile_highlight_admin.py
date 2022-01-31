from django.contrib.gis import admin
from adminsortable2.admin import SortableAdminMixin

from ... import models
from ..forms import ProfileHighlightForm

from wazimap_ng.general.widgets import customTitledFilter, description
from wazimap_ng.datasets.models import Indicator, Dataset
from wazimap_ng.general.services import permissions
from wazimap_ng.general.admin.admin_base import BaseAdminModel, HistoryAdmin
from wazimap_ng.general.admin import filters


@admin.register(models.ProfileHighlight)
class ProfileHighlightAdmin(SortableAdminMixin, BaseAdminModel, HistoryAdmin):

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