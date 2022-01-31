import json

from django.contrib import admin, messages
from django.contrib.admin.options import DisallowedModelAdminToField
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.admin.utils import model_ngettext, unquote
from django.contrib.admin import helpers
from django.contrib.auth import get_permission_codename
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from django_q.tasks import async_task

from wazimap_ng.general.services import permissions
from simple_history.admin import SimpleHistoryAdmin
from wazimap_ng.datasets.models import Dataset


class HistoryAdmin(SimpleHistoryAdmin):
    exclude_change_fields = ["change_reason"]
    history_list_display = ["changed_fields"]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        new_fieldsets = list(fieldsets)
        fields = ['change_reason']
        new_fieldsets.append(['Change reason', { 'fields': fields }])
        return new_fieldsets

    def save_model(self, request, obj, form, change):
        change_reason = form.cleaned_data.get("change_reason", None)
        if change_reason:
            obj._change_reason = change_reason
        super().save_model(request, obj, form, change)

    def changed_fields(self, record):
        prev_record = record.prev_record
        if prev_record:
            delta = record.diff_against(prev_record)
            changes = [change.field for change in delta.changes]
            if not changes:
                return "-"
            return ", ".join(changes)
        return 'Not Available'


class BaseAdminModel(admin.ModelAdmin):
    """

    Base Admin Model Permissions

    custom_queryset_fun:
        * This is the function you want to call to get your queryset.
        * Set to None if you want original queryset or change name and
          add new custom queryset function in services/permissions

        This custom queryset function will call and fetch queryset filters
        dynamically. We can add dynamic filters in service/custom_permission/filter_queryset

        Name of the custom filter should be : get_filters_for_{model_name}

    exclude_fk_filters:
        * This is the list of foreign key to exclude from filtering fks
        If fk for a model is not added here than it will be filtered out
        using get_custom_queryset function.

        We can further filter queryset using dynamic function definition for model
        in service/custom_permission/filter_fk_queryset.

        Name of the custom fk filter should be : get_filters_for_{model_name}

    permissions:
        * View permission is handled by get_queryset.
        User will not be able to edit/view object if it's not available in queryset

        Right now change/delete is working on a premise that we can only edit
        private type data that user has permission to edit.

        If we want to define cutsom permissions we have to define dynamic permission
        function in service/custom_permission/custom_permissions

        Name of the custom permission should be : user_has_perm_for_{app_label}_{model_name}

    """

    custom_queryset_func = 'get_custom_queryset'
    exclude_fk_filters = []
    help_texts = []
    exclude_common_list_display = False
    common_list_display = ("created", "updated",)
    date_hierarchy = "created"

    def __init__(self, model, admin_site):
        if not self.exclude_common_list_display:
            list_display = self.list_display
            self.list_display = list_display + self.common_list_display
        super().__init__(model, admin_site)

    def has_delete_permission(self, request, obj=None):
        has_perm = super().has_delete_permission(request, obj)
        if has_perm:
            return permissions.has_permission(request.user, obj, "delete")
        return has_perm

    def has_change_permission(self, request, obj=None):
        has_perm = super().has_change_permission(request, obj)
        if has_perm:
            return permissions.has_permission(request.user, obj, "change")
        return has_perm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name not in self.exclude_fk_filters and not request.user.is_superuser:
            kwargs["queryset"] = getattr(
                permissions, "get_custom_fk_queryset"
            )(request.user, db_field.related_model)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if self.custom_queryset_func:
            return getattr(permissions, self.custom_queryset_func)(self.model, request.user)
        return qs

    def _get_help_text(self, field):
        widget = field.widget
        if widget.__class__.__name__ == "Select":
            choices = [
                choice[0] for choice in widget.choices
            ]

        elif widget.__class__.__name__ == "RelatedFieldWidgetWrapper":
            choices = [
                choice[1] for choice in widget.choices
            ]
        else:
            choices = []
        return mark_safe(render_to_string(
            'admin/custom_help_texts.html', {'choices': choices}
        ))

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.current_user = request.user

        for field_name in self.help_texts:
            if field_name in form.base_fields:
                form.base_fields[field_name].help_text = self._get_help_text(
                    form.base_fields[field_name]
                )
        return form
