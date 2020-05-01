from django.contrib.gis import admin
from django.contrib.postgres import fields
from adminsortable2.admin import SortableAdminMixin

from ... import models
from ..forms import ProfileIndicatorAdminForm

from wazimap_ng.admin_utils import customTitledFilter, description, SortableWidget
from wazimap_ng.datasets.models import Indicator, Dataset
from wazimap_ng.general.services import permissions

@admin.register(models.ProfileIndicator)
class ProfileIndicatorAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_filter = (
        ('profile__name', customTitledFilter('Profile')),
        ('subcategory__category__name', customTitledFilter('Category')),
        "subcategory",
    )

    list_display = (
        "profile",
        "label", 
        description("Indicator", lambda x: x.indicator.name), 
        description("Category", lambda x: x.subcategory.category.name),
        "subcategory",
        "order",
    )

    fieldsets = (
        ("Database fields (can't change after being created)", {
            'fields': ('profile', 'indicator')
        }),
        ("Profile fields", {
          'fields': ('label', 'subcategory', 'description', 'choropleth_method')
        }),
        ("Subindicators", {
          'fields': ('subindicators',)
        })
    )

    form = ProfileIndicatorAdminForm

    formfield_overrides = {
        fields.JSONField: {"widget": SortableWidget},
    }

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile",) + self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.subindicators = obj.indicator.subindicators
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "profile":
            kwargs["queryset"] = permissions.get_objects_for_user(request.user, "view", models.Profile)

        if db_field.name == "indicator":
            profiles = permissions.get_objects_for_user(request.user, "view", models.Profile)
            herarchies = profiles.values_list("geography_hierarchy")
            datasets = permissions.get_objects_for_user(request.user, "view", Dataset)
            kwargs["queryset"] = Indicator.objects.filter(
                dataset__in=datasets.filter(geography_hierarchy__in=herarchies)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        profiles = permissions.get_objects_for_user(request.user, "view", models.Profile)
        return qs.filter(profile__in=profiles)