from django.contrib import admin, messages
from django.contrib.admin.options import DisallowedModelAdminToField
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.admin.utils import model_ngettext, unquote
from django.contrib.admin import helpers
from django.contrib.auth import get_permission_codename

from django_q.tasks import async_task

from wazimap_ng.general.services import permissions


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

    def has_delete_permission(self, request, obj=None):
        return permissions.has_permission(request.user, obj, "delete")

    def has_change_permission(self, request, obj=None):
        return permissions.has_permission(request.user, obj, "change")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name not in self.exclude_fk_filters and  self.custom_queryset_func:
            kwargs["queryset"] = getattr(
                permissions, "get_custom_fk_queryset"
            )(request.user, db_field.related_model)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if self.custom_queryset_func:
            return getattr(permissions, self.custom_queryset_func)(request.user, self.model, qs)
        return qs