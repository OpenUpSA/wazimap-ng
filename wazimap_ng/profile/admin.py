from django.contrib.gis import admin
from django import forms

from . import models
from wazimap_ng.datasets.models import Indicator

@admin.register(models.Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ("profile",)
    list_filter = ("profile",)

@admin.register(models.Licence)
class LicenceAdmin(admin.ModelAdmin):
    pass


class ProfileKeyMetricsForm(forms.ModelForm):
    MY_CHOICES = (
        (None, '-------------'),
    )

    subindicator = forms.ChoiceField(choices=MY_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'variable' in self.data:
            try:
                variable_id = int(self.data.get('variable'))
                self.fields['subindicator'].choices = [
                	[subindicator, subindicator] for subindicator in Indicator.objects.filter(id=variable_id).first().subindicators
                ]
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.subindicator:
            self.fields['subindicator'].choices = [
            	[subindicator, subindicator] for subindicator in Indicator.objects.filter(id=self.instance.variable.pk).first().subindicators
            ]

@admin.register(models.ProfileKeyMetrics)
class MyModelAdmin(admin.ModelAdmin):
    fields = ('variable', 'subcategory', 'subindicator', 'denominator',)
    list_display = ('variable',)
    form = ProfileKeyMetricsForm


    class Media:
        js = ("/static/js/variable_subindicators.js",)