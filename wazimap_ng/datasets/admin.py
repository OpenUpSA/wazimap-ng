from django.contrib import admin
from django.contrib.postgres import fields
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from django_json_widget.widgets import JSONEditorWidget

from django_q.tasks import async_task

from . import models

admin.site.register(models.IndicatorCategory)
admin.site.register(models.IndicatorSubcategory)
admin.site.register(models.Dataset)
admin.site.register(models.Profile)


def customTitledFilter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


@admin.register(models.Geography)
class GeographyAdmin(TreeAdmin):
    form = movenodeform_factory(models.Geography)
    list_display = (
        "name", "code", "level"
    )

    list_filter = ("level",)


def description(description, func):
    func.short_description = description
    return func


@admin.register(models.ProfileIndicator)
class ProfileIndicatorAdmin(admin.ModelAdmin):
    list_filter = (
        ('profile__name', customTitledFilter('Profile')),
        ('indicator__name', customTitledFilter('Indicator')),
        ('subcategory__category__name', customTitledFilter('Category')),
        "subcategory",
        "universe",
    )

    list_display = (
        "profile", 
        "name", 
        "label", 
        description("Indicator", lambda x: x.indicator.name), 
        description("Category", lambda x: x.subcategory.category.name),
        "subcategory",
        "universe",
        "key_metric",
    )

    fieldsets = (
        ("Database fields (can't change after being created)", {
            'fields': ('profile', 'universe', 'name', 'indicator')
        }),
        ("Profile fields", {
          'fields': ('label', 'subcategory', 'key_metric')
        })
    )


    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile", "universe", "name") + self.readonly_fields
        return self.readonly_fields

@admin.register(models.ProfileHighlight)
class ProfileHighlightAdmin(admin.ModelAdmin):
    list_filter = (
        ("profile__name", customTitledFilter("Profile")),
        ("indicator__name", customTitledFilter("Indicator")),
        "universe",
    )

    list_display = (
        "profile", 
        "name", 
        "label", 
        description("Indicator", lambda x: x.indicator.name), 
        "universe",
    )

    fieldsets = (
        ("Database fields (can't change after being created)", {
            "fields": ("profile", "universe", "name", "indicator")
        }),
        ("Profile fields", {
          "fields": ("label", "value")
        })
    )


    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile", "universe", "name") + self.readonly_fields
        return self.readonly_fields

@admin.register(models.Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Universe)
class UniverseAdmin(admin.ModelAdmin):
  formfield_overrides = {
    fields.JSONField: {"widget": JSONEditorWidget},
  }


@admin.register(models.DatasetFile)
class DatasetFileAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        is_created = obj.pk == None and change == False
        super().save_model(request, obj, form, change)
        if is_created:
            async_task("wazimap_ng.datasets.tasks.process_uploaded_file", obj)

        return obj
    
