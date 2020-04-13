from django.contrib.gis import admin

from ... import models
from ..forms import ProfileKeyMetricsForm
from wazimap_ng.admin_utils import customTitledFilter, description 

@admin.register(models.ProfileKeyMetrics)
class ProfileKeyMetricsAdmin(admin.ModelAdmin):
    fields = ('profile', 'variable', 'subcategory', 'subindicator', 'denominator',)
    list_display = ('variable',)
    form = ProfileKeyMetricsForm

    list_filter = (
        ('subcategory__category__profile', customTitledFilter('Profile')),
    )


    class Media:
        js = (
            "/static/js/jquery-ui.min.js",
            "/static/js/variable_subindicators.js",
        )