import json

from django.forms.widgets import Widget
from django.contrib import admin
from guardian.shortcuts import (
    get_group_perms, get_perms_for_model, get_groups_with_perms
)

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


class GroupPermissionWidget(Widget):
    template_name = 'widgets/GroupPermissionWidget.html'

    def init_parameters(current_user, instance, permission_type):
        self.current_user = current_user
        self.target = instance
        self.permission_type = permission_type

    def get_context(self, name, value, attrs=None):

        user = self.current_user
        user_groups = user.groups.all()
        target = self.target
        model_permissions = {
            c.split("_")[0] : c for c in get_perms_for_model(self.target).values_list("codename", flat=True)
        }
        selected_groups = get_groups_with_perms(self.target)
        selected_group_ids = selected_groups.values_list("id", flat=True)

        selected_group_list = []
        if self.target.id:
            for group in selected_groups:
                perms = get_group_perms(group, self.target)
                data = {"group": group, "perms": perms}
                if group in user_groups:
                    selected_group_list.insert(0, data)
                else:
                    selected_group_list.append(data)

        other_group_list = [
            {"group": group, "perms": []} for group in self.choices.queryset.exclude(id__in=selected_group_ids)
        ]

        return {"widget": {
            'name': name,
            'values': value,
            "user_groups": user_groups,
            "permission_type": self.permission_type,
            "permissions": model_permissions,
            "groups": selected_group_list + other_group_list
        }}
        
    class Media:
        css = {"all": ("/static/css/group-permission-widget.css",)}
        js = ("/static/js/jquery-ui.min.js", "/static/js/group-permission-widget.js",)


