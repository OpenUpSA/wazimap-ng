from django.forms import ModelForm
from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from .models import IndicatorCategory, IndicatorSubcategory, Indicator, Dataset, Geography, ProfileIndicator

admin.site.register(IndicatorCategory)
admin.site.register(IndicatorSubcategory)
admin.site.register(Dataset)

def customTitledFilter(title):
   class Wrapper(admin.FieldListFilter):
       def __new__(cls, *args, **kwargs):
           instance = admin.FieldListFilter.create(*args, **kwargs)
           instance.title = title
           return instance
   return Wrapper

class GeographyAdmin(TreeAdmin):
    form = movenodeform_factory(Geography)
    list_display = (
        "name", "code", "level"
    )

    list_filter = ("level",)

def description(description, func):
    func.short_description = description
    return func

class ProfileIndicatorAdmin(admin.ModelAdmin):
    list_filter = (
        ('profile__name', customTitledFilter('Profile')),
        ('indicator__name', customTitledFilter('Indicator')),
        ('subcategory__category__name', customTitledFilter('Category')),
        "subcategory",
    )

    list_display = (
        "profile", 
        description("Indicator", lambda x: x.indicator.name), 
        description("Category", lambda x: x.subcategory.category.name),
        "subcategory",
        "key_metric",
    )

admin.site.register(Geography, GeographyAdmin)
admin.site.register(ProfileIndicator, ProfileIndicatorAdmin)



class IndicatorAdmin(admin.ModelAdmin):
    pass

admin.site.register(Indicator, IndicatorAdmin)
