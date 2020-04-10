from django.contrib import admin
from django.contrib.postgres import fields
from django import forms

from .. import models
from .. import widgets
from .utils import customTitledFilter, description
from urllib.parse import unquote


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
        fields.JSONField: {"widget": widgets.SortableWidget},
    }

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile",) + self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.subindicators = obj.indicator.subindicators
        super().save_model(request, obj, form, change)