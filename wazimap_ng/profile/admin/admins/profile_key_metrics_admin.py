from django.contrib.gis import admin

from ... import models
from ..forms import ProfileKeyMetricsForm

@admin.register(models.ProfileKeyMetrics)
class ProfileKeyMetricsAdmin(admin.ModelAdmin):
    fields = ('variable', 'subcategory', 'subindicator', 'denominator',)
    list_display = ('variable',)
    form = ProfileKeyMetricsForm


    class Media:
        js = (
            "/static/js/jquery-ui.min.js",
            "/static/js/variable_subindicators.js",
        )