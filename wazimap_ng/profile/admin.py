from django.contrib.gis import admin
from django import forms
from django.contrib.postgres import fields
from django.contrib.admin import FieldListFilter

from . import models
from wazimap_ng.datasets.models import Indicator
from ..admin_utils import customTitledFilter, description, SortableWidget

@admin.register(models.Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ("profile",)
    list_filter = ("profile",)

@admin.register(models.Licence)
class LicenceAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.IndicatorCategory)

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
                	[subindicator['id'], subindicator['label']] for subindicator in list(Indicator.objects.filter(id=variable_id).first().subindicators)
                ]
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            print(self.instance.subindicator)
            print(self.instance.pk)
            self.fields['subindicator'].choices = [
            	[subindicator['id'], subindicator['label']] for subindicator in Indicator.objects.filter(id=self.instance.variable.pk).first().subindicators
            ]

@admin.register(models.ProfileKeyMetrics)
class MyModelAdmin(admin.ModelAdmin):
    fields = ('variable', 'subcategory', 'subindicator', 'denominator',)
    list_display = ('variable',)
    form = ProfileKeyMetricsForm


    class Media:
        js = ("/static/js/variable_subindicators.js",)


class ProfileHighlightForm(forms.ModelForm):
    MY_CHOICES = (
        (None, '-------------'),
    )

    subindicator = forms.ChoiceField(choices=MY_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_indicators = models.Indicator.objects.all()

        if 'indicator' in self.data:
            try:
                variable_id = int(self.data.get('indicator'))
                self.fields['subindicator'].choices = [
                    [subindicator["id"], subindicator["label"]] 
                    for subindicator in all_indicators.filter(id=variable_id).first().subindicators
                ]
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['subindicator'].choices = [
                [subindicator["id"], subindicator["label"]]
                for subindicator in all_indicators.filter(id=self.instance.indicator.pk).first().subindicators
            ]

@admin.register(models.ProfileHighlight)
class ProfileHighlightAdmin(admin.ModelAdmin):
    list_filter = (
        ("profile__name", customTitledFilter("Profile")),
        ("indicator__name", customTitledFilter("Indicator")),
    )

    list_display = (
        "profile", 
        "name", 
        "label", 
        description("Indicator", lambda x: x.indicator.name), 
    )

    fieldsets = (
        ("Database fields (can't change after being created)", {
            "fields": ("profile", "name", "indicator")
        }),
        ("Profile fields", {
          "fields": ("label", "subindicator")
        })
    )
    form = ProfileHighlightForm

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile", "name") + self.readonly_fields
        return self.readonly_fields



    class Media:
        js = ("/static/js/variable_subindicators.js",)


class ProfileIndicatorAdminForm(forms.ModelForm):
    class Meta:
        model = models.ProfileIndicator
        fields = '__all__'

    def clean_subindicators(self):
        if self.instance.pk:
            values = self.instance.indicator.subindicators
            order = self.cleaned_data['subindicators']
            return [values[i] for i in order] if order else values
        return []

@admin.register(models.ProfileIndicator)
class ProfileIndicatorAdmin(admin.ModelAdmin):
    list_filter = (
        ('profile__name', customTitledFilter('Profile')),
        ('indicator__name', customTitledFilter('Indicator')),
        ('subcategory__category__name', customTitledFilter('Category')),
        "subcategory",
    )

    list_display = (
        "profile",
        "label", 
        description("Indicator", lambda x: x.indicator.name), 
        description("Category", lambda x: x.subcategory.category.name),
        "subcategory",
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