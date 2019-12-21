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
        "subcategory"
    )

admin.site.register(Geography, GeographyAdmin)
admin.site.register(ProfileIndicator, ProfileIndicatorAdmin)


from django_select2.forms import Select2TagWidget, Select2Widget
class ArrayFieldWidget(Select2TagWidget):

    def render_options(self, *args, **kwargs):
        try:
            selected_choices, = args
        except ValueError:  # Signature contained `choices` prior to Django 1.10
            choices, selected_choices = args
        output = ['<option></option>' if not self.is_required and not self.allow_multiple_selected else '']
        selected_choices = {force_text(v) for v in selected_choices.split(',')}
        choices = {(v, v) for v in selected_choices}
        for option_value, option_label in choices:
            output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        return ",".join(values)

class MyWidget(Select2Widget):

    def value_from_datadict(self, data, files, name):
        values = super(MyWidget, self).value_from_datadict(data, files, name)
        return ",".join(values)

    def optgroups(self, name, value, attrs=None):
        values = value[0].split(',') if value[0] else []
        selected = set(values)
        subgroup = [self.create_option(name, v, v, selected, i) for i, v in enumerate(values)]
        return [(None, subgroup, 0)]

class IndicatorArrayFieldForm(ModelForm):

    class Meta:
        model = Indicator
        fields = ['dataset', 'groups', 'name', 'label']
        widgets = {
            'groups': MyWidget
        }

class IndicatorAdmin(admin.ModelAdmin):
    pass
    #def get_form(self, request, obj=None, **kwargs):
    #    form = IndicatorArrayFieldForm
    #    return form

admin.site.register(Indicator, IndicatorAdmin)
