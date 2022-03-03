import json

from django.forms.widgets import Widget
from django.contrib import admin
from guardian.shortcuts import (
    get_group_perms, get_perms_for_model, get_groups_with_perms
)
from django import forms

from wazimap_ng.general.services import permissions

def customTitledFilter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper
    
def description(description, func):
    func.short_description = description
    return func


class SortableWidget(Widget):
    template_name = 'widgets/SortableWidget.html'

    class Media:
        css = {'all': ("/static/css/jquery-ui.min.css", "/static/css/sortable-widget.css",)}
        js = ("/static/js/jquery-ui.min.js", "/static/js/sortable-widget.js",)

    def get_context(self, name, value, attrs=None):
        values_list = []
        values = json.loads(value)

        return {'widget': {
            'name': name,
            'values': values
        }}

class VariableFilterWidget(Widget):
    template_name = 'widgets/VariableFilterWidget.html'

    class Media:
        css = {'all': ("/static/css/variable-filter-widget.css",)}
        js = ("/static/js/variable-filter-widget.js",)

    def get_context(self, name, value, attrs=None):

        CHOICES = [('public', 'Public'), ('private', 'Private')]
        choice_field = forms.fields.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
        queryset = self.choices.queryset.order_by(
            'dataset__profile__name',
            'dataset__name',
            'name'
        )
        selected_permission = "public"
        if value:
            value = queryset.get(id=value)
            selected_permission = value.dataset.permission_type

        return {
            'name': name,
            'value': value,
            'choices': queryset,
            'permission_type': selected_permission,
            "choice_field": choice_field.widget.render(f"{name}_variable_type", selected_permission)
        }