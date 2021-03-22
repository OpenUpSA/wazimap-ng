from adminsortable2.admin import SortableAdminMixin
from django.contrib.gis import admin
from django.db.models import ForeignKey
from django.db.models.functions import Concat
from django.forms.models import ModelForm
from django.http.request import HttpRequest

from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.widgets import description
from wazimap_ng.profile.models import ProfileIndicator

from ..forms import ProfileIndicatorAdminForm


class CategoryIndicatorFilter(filters.CategoryFilter):
    parameter_name = 'subcategory__category__id'


@admin.register(ProfileIndicator)
class ProfileIndicatorAdmin(SortableAdminMixin, BaseAdminModel):
    list_filter = (
        filters.ProfileNameFilter,
        CategoryIndicatorFilter,
        filters.SubCategoryFilter,
    )

    exclude_common_list_display = True
    list_display = (
        "profile",
        "label",
        description("Indicator", lambda x: x.indicator.name),
        description("Category", lambda x: x.subcategory.category.name),
        "subcategory",
        "created",
        "updated",
        "order",
    )

    fieldsets = (
        ("Database fields (can't change after being created)", {
            'fields': ('profile', 'indicator')
        }),
        ("Profile fields", {
            'fields': ('label', 'subcategory', 'description', 'choropleth_method')
        }),
        ("Charts", {
            'fields': ('chart_configuration',)
        })
    )
    search_fields = ("label", )

    form = ProfileIndicatorAdminForm

    help_texts = ["choropleth_method", ]

    class Media:
        js = ("/static/js/profile-indicator-admin.js",)

    def get_readonly_fields(self, request: HttpRequest, obj: ProfileIndicator = None):
        if obj:  # editing an existing object
            return ("profile",) + self.readonly_fields
        return self.readonly_fields

    def save_model(self, request: HttpRequest, obj: ProfileIndicator, form: ModelForm, change: bool):
        if not change:
            obj.subindicators = obj.indicator.subindicators
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field: ForeignKey, request: HttpRequest, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "indicator":
            qs = field.queryset.annotate(
                display_name=Concat('dataset__name', 'name')
            ).order_by("display_name")
            field.queryset = qs
        return field
