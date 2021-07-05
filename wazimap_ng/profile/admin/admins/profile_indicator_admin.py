from django.contrib.gis import admin
from django.contrib.postgres import fields
from adminsortable2.admin import SortableAdminMixin

from ... import models
from ..forms import ProfileIndicatorAdminForm

from wazimap_ng.general.widgets import customTitledFilter, description
from wazimap_ng.datasets.models import Indicator, Dataset
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.admin import filters
from django.db.models.functions import Concat

class CategoryIndicatorFilter(filters.CategoryFilter):
    parameter_name = 'subcategory__category__id'

@admin.register(models.ProfileIndicator)
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
        ("Qualitative Content", {
          'fields': ('content_type', 'content_indicator')
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

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
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

            if obj.content and obj.content.indicator:
                form.base_fields["content_indicator"].initial = obj.content.indicator_id
                form.base_fields["content_type"].initial = obj.content.content_type

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

    def save_model(self, request, obj, form, change):
        is_new = obj.pk == None
        content_indicator = form.cleaned_data.get("content_indicator", None)
        content_type = form.cleaned_data.get("content_type", None)
        if not change:
            if content_indicator:
                obj.content = models.Content.objects.create(
                    indicator=content_indicator,
                    content_type=content_type
                )
        else:
            if(
                "content_indicator" in form.changed_data or 
                "content_type" in form.changed_data
            ):
                content, created = models.Content.objects.update_or_create(
                    indicator=content_indicator,
                    content_type=content_type
                )
                obj.content = content

        super().save_model(request, obj, form, change)
