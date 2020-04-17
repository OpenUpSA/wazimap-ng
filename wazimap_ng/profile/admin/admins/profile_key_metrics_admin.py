from django.contrib.gis import admin
from adminsortable2.admin import SortableAdminMixin

from ... import models
from ..forms import ProfileKeyMetricsForm
from wazimap_ng.admin_utils import customTitledFilter, description
from guardian.shortcuts import get_objects_for_user

@admin.register(models.ProfileKeyMetrics)
class ProfileKeyMetricsAdmin(SortableAdminMixin, admin.ModelAdmin):
    #fields = ("profile", "variable", "subcategory", "subindicator", "denominator", "label", "order")
    list_display = (
        description("Variable", lambda x: x.variable.name),
        description("Profile", lambda x: x.subcategory.category.profile.name),
        description("Subcategory", lambda x: x.subcategory.name),
        description("Category", lambda x: x.subcategory.category.name),
        "order"
    )
    form = ProfileKeyMetricsForm

    list_filter = (
        ("subcategory__category__profile", customTitledFilter("Profile")),
        ('subcategory__category__name', customTitledFilter('Category')),
        ('subcategory__name', customTitledFilter('Subcategory')),
    )


    class Media:
        js = (
            "/static/js/jquery-ui.min.js",
            "/static/js/variable_subindicators.js",
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "profile":
            profiles = models.Profile.objects.all().exclude(profile_type="private")
            profiles |= get_objects_for_user(request.user, 'profile.view_profile', accept_global_perms=False)
            kwargs["queryset"] = profiles
        return super().formfield_for_foreignkey(db_field, request, **kwargs)