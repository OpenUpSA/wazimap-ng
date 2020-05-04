import json

from django.forms.widgets import Widget
from django.contrib import admin
from guardian.shortcuts import (
    get_group_perms, get_perms_for_model, get_groups_with_perms
)

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


class GroupPermissionWidget(Widget):
    template_name = 'widgets/GroupPermissionWidget.html'

    def init_parameters(self, current_user, instance, permission_type):
        self.current_user = current_user
        self.target = instance
        self.permission_type = permission_type

    def get_groups(self, obj, user):
        all_groups = []
        groups_packed = []
        
        if obj.id:
            groups_with_permission = permissions.get_user_groups_with_permission_on_object(obj, user)
            groups_without_permission = permissions.get_user_groups_without_permission_on_object(obj, user)
            all_groups += groups_with_permission + groups_without_permission
            all_permissions = [get_group_perms(g, obj) for g in all_groups]
            groups_packed = [{"group": g, "perms": p} for (g, p) in zip(all_groups, all_permissions)]

        other_groups = [g for g in self.choices.queryset.exclude(id__in=[gr.id for gr in all_groups])]
        other_packed = [{"group": g, "perms": []} for g in other_groups]

        return groups_packed + other_packed

    def get_context(self, name, value, attrs=None):
        packed = self.get_groups(self.target, self.current_user)

        model_permissions = {
            c.split("_")[0] : c for c in get_perms_for_model(self.target).values_list("codename", flat=True)
        }

        return {
            "widget": {
                "name": name,
                "values": value,
                "user_groups": self.current_user.groups.all(),
                "permission_type": self.permission_type,
                "permissions": model_permissions,
                "groups": packed
            }
        }
        
    class Media:
        css = {"all": ("/static/css/group-permission-widget.css",)}
        js = ("/static/js/jquery-ui.min.js", "/static/js/group-permission-widget.js",)
