import json
import ast

from django.forms.widgets import Widget
from django.template import Context, Template
from django.utils.safestring import mark_safe


class SortableWidget(Widget):
    template_name = 'widgets/SortableWidget.html'

    class Media:
        css = {'all': (
            "/static/css/jquery-ui.min.css", "/static/css/sortable-widget.css",)
        }
        js = ("/static/js/jquery-ui.min.js", "/static/js/sortable-widget.js",)

    def get_context(self, name, value, attrs=None):
        values_list = value.split("|") if value else []
        return {'widget': {
            'name': name,
            'values': {"list": values_list, "text": mark_safe(value)},
        }}