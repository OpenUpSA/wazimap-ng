from adminsortable2.admin import SortableAdminMixin
from django.contrib.gis import admin
from django.forms.forms import Form
from django.http.request import HttpRequest

from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.widgets import description
from wazimap_ng.profile.models import IndicatorSubcategory, ProfileKeyMetrics

from ..forms import ProfileKeyMetricsForm


class CategoryMetricsFilter(filters.CategoryFilter):
    parameter_name = 'subcategory__category__id'


@admin.register(ProfileKeyMetrics)
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

    def get_form(self, request: HttpRequest, obj: ProfileKeyMetrics = None, **kwargs) -> Form:
        form = super().get_form(request, obj, **kwargs)
        qs = form.base_fields["subcategory"].queryset
        if obj:
            profile_id = obj.profile_id
            if request.method == "POST":
                profile_id = request.POST.get("profile", profile_id)
            qs = IndicatorSubcategory.objects.filter(
                category__profile_id=profile_id
            )
        elif not obj and request.method == "GET":
            qs = qs = IndicatorSubcategory.objects.none()

        form.base_fields["subcategory"].queryset = qs

        return form
