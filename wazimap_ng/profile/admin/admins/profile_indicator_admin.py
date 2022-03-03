from django.contrib.gis import admin
from django.contrib.postgres import fields
from adminsortable2.admin import SortableAdminMixin

from ... import models
from ..forms import ProfileIndicatorAdminForm

from wazimap_ng.general.widgets import customTitledFilter, description
from wazimap_ng.datasets.models import Indicator, Dataset
from wazimap_ng.general.admin.admin_base import BaseAdminModel, HistoryAdmin
from wazimap_ng.general.admin import filters
from django.db.models.functions import Concat


class CategoryIndicatorFilter(filters.CategoryFilter):
    parameter_name = 'subcategory__category__id'


@admin.register(models.ProfileIndicator)
class ProfileIndicatorAdmin(SortableAdminMixin, BaseAdminModel, HistoryAdmin):
    list_filter = (
        filters.ProfileNameFilter,
        CategoryIndicatorFilter,
        filters.SubCategoryFilter,
    )

    exclude_common_list_display = True
    list_display = (
        "label",
        description("Variable", lambda x: x.indicator.name),
        "profile",
        description("Category", lambda x: x.subcategory.category.name),
        "subcategory",
        "created",
        "updated",
        "order",
    )

    fieldsets = (
        ("Profile fields", {
            'fields': (
            'profile', 'subcategory', 'label', 'indicator', 'content_type', 'choropleth_method', 'description')
        }),
        ("Charts", {
            'fields': ('chart_configuration',)
        })
    )
    search_fields = ("label",)

    form = ProfileIndicatorAdminForm

    help_texts = ["choropleth_method", ]

    class Media:
        js = ("/static/js/profile-indicator-admin.js",)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ("profile",) + self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.subindicators = obj.indicator.subindicators
        super().save_model(request, obj, form, change)

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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "indicator":
            qs = field.queryset.annotate(
                display_name=Concat('dataset__name', 'name')
            ).order_by("display_name")
            field.queryset = qs
        return field
