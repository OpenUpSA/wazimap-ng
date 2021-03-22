from __future__ import annotations

import json
from typing import Callable, Dict

from django import forms
from django.contrib import admin
from django.forms.widgets import Widget


def customTitledFilter(title: str):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


def description(description: str, func: Callable):
    func.short_description = description
    return func


class SortableWidget(Widget):
    template_name = 'widgets/SortableWidget.html'

    class Media:
        css = {'all': ("/static/css/jquery-ui.min.css", "/static/css/sortable-widget.css",)}
        js = ("/static/js/jquery-ui.min.js", "/static/js/sortable-widget.js",)

    def get_context(self, name: str, value: str, attrs=None) -> Dict:
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

    def get_context(self, name: str, value: str, attrs=None) -> Dict:

        CHOICES = [('public', 'Public'), ('private', 'Private')]
        choice_field = forms.fields.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
        queryset = self.choices.queryset
        selected_permission = "public"
        if value:
            value = queryset.get(id=value)
            selected_permission = value.dataset.permission_type
        return {
            'name': name,
            'value': value,
            'choices': queryset,
            'permission_type': selected_permission,
            "choice_field": choice_field.widget.render("variable_type", selected_permission)
        }
