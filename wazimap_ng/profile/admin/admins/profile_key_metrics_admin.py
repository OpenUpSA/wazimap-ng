from django.contrib.gis import admin
from adminsortable2.admin import SortableAdminMixin

from ... import models
from ..forms import ProfileKeyMetricsForm
from wazimap_ng.general.widgets import customTitledFilter, description
from wazimap_ng.datasets.models import Indicator, Dataset
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.admin import filters



class CategoryMetricsFilter(filters.CategoryFilter):
    parameter_name = 'subcategory__category__id'

@admin.register(models.ProfileKeyMetrics)
class ProfileKeyMetricsAdmin(SortableAdminMixin, BaseAdminModel):

    exclude_common_list_display = True
    list_display = (
        "label",
        description("Variable", lambda x: x.variable.name),
        description("Profile", lambda x: x.subcategory.category.profile.name),
        description("Subcategory", lambda x: x.subcategory.name),
        description("Category", lambda x: x.subcategory.category.name),
        "created",
        "updated",
        "order"
    )
    form = ProfileKeyMetricsForm

    list_filter = (
        filters.ProfileNameFilter,
        CategoryMetricsFilter,
        filters.SubCategoryFilter,
    )

    help_texts = ["denominator", ]

    fields = ["profile", "variable", "subindicator", "subcategory", "denominator", "label"]
    search_fields = ("label", )


    class Media:
        js = (
            "/static/js/variable_subindicators.js",
        )