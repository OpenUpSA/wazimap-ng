from django.contrib.gis import admin
from adminsortable2.admin import SortableAdminMixin

from ... import models
from ..forms import ProfileKeyMetricsForm
from wazimap_ng.general.widgets import customTitledFilter, description
from wazimap_ng.datasets.models import Indicator, Dataset
from wazimap_ng.general.admin.admin_base import BaseAdminModel, HistoryAdmin
from wazimap_ng.general.admin import filters


class CategoryMetricsFilter(filters.CategoryFilter):
    parameter_name = 'subcategory__category__id'


@admin.register(models.ProfileKeyMetrics)
class ProfileKeyMetricsAdmin(SortableAdminMixin, BaseAdminModel, HistoryAdmin):
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

    fieldsets = (
        ("Profile fields", {
            "fields": ("profile", "subcategory", "label", "variable", "subindicator", "denominator")
        }),
    )
    form = ProfileKeyMetricsForm

    list_filter = (
        filters.ProfileNameFilter,
        CategoryMetricsFilter,
        filters.SubCategoryFilter,
    )

    help_texts = ["denominator", ]

    search_fields = ("label",)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ("profile",) + self.readonly_fields
        return self.readonly_fields

    class Media:
        js = (
            "/static/js/variable_subindicators.js",
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        qs = form.base_fields["subcategory"].queryset
        if obj:
            profile_id = obj.profile_id
            if request.method == "POST":
                profile_id = request.POST.get("profile", profile_id)
            qs = models.IndicatorSubcategory.objects.filter(
                category__profile_id=profile_id
            )
        elif not obj and request.method == "GET":
            qs = qs = models.IndicatorSubcategory.objects.none()

        form.base_fields["subcategory"].queryset = qs

        return form
