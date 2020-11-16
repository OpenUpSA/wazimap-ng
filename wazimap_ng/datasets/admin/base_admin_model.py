from django.contrib.admin.options import DisallowedModelAdminToField
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.admin.utils import model_ngettext, unquote
from django.contrib.admin import helpers

from django_q.tasks import async_task
from notifications.signals import notify

from wazimap_ng.general.admin.admin_base import BaseAdminModel


def delete_selected_data(modeladmin, request, queryset):
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied

    opts = modeladmin.model._meta
    app_label = opts.app_label
    objects_name = model_ngettext(queryset)

    if request.POST.get('post'):
        if not modeladmin.has_delete_permission(request):
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                obj_display = str(obj)
                modeladmin.log_deletion(request, obj, obj_display)

            task = async_task(
                'wazimap_ng.datasets.tasks.delete_data',
                queryset,
                objects_name,
                task_name=f"Deleting data: {objects_name}",
                hook="wazimap_ng.datasets.hooks.process_task_info",
                key=request.session.session_key,
                type="delete",
                notify=True,
            )
            notify.send(
                request.user,
                recipient=request.user,
                verb=F"Initiating bulk delete process for",
                task_id=task,
                level="in_progress",
                type="delete",
                object_name=objects_name,
                count=queryset.count(),
                bulk=True
            )
        return None

    context = {
        **modeladmin.admin_site.each_context(request),
        'title': "Are you sure?",
        'objects_name': str(objects_name),
        'deletable_objects': [],
        'model_count': "",
        'queryset': queryset,
        'opts': opts,
        'media': modeladmin.media,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }

    return TemplateResponse(
        request,
        "admin/datasets_delete_selected_confirmation.html",
        context,
    )


delete_selected_data.short_description = "Delete selected objects"


class DatasetBaseAdminModel(BaseAdminModel):

    actions = [delete_selected_data]

    def delete_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        app_label = opts.app_label

        to_field = request.POST.get("_to_field", request.GET.get("_to_field"))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

        obj = self.get_object(request, unquote(object_id), to_field)

        if not self.has_delete_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        object_name = str(opts.verbose_name)

        if request.POST:  # The user has confirmed the deletion.
            if not self.has_delete_permission(request, obj):
                raise PermissionDenied
            obj_display = str(obj)
            attr = str(to_field) if to_field else opts.pk.attname
            obj_id = obj.serializable_value(attr)
            self.log_deletion(request, obj, obj_display)
            task = async_task(
                "wazimap_ng.datasets.tasks.delete_data",
                obj,
                object_name,
                task_name=f"Deleting data: {obj.name}",
                hook="wazimap_ng.datasets.hooks.process_task_info",
                key=request.session.session_key,
                type="delete",
                notify=True
            )
            notify.send(
                request.user, recipient=request.user,
                verb="We run data deletion in background because of related data and caches. We will let you know when processing is done",
                task_id=task,
                level="in_progress",
                type="delete",
                object_name=object_name,
                name=obj.name,
                bulk=False
            )

            return self.response_delete(request, obj_display, obj_id)

        context = {
            **self.admin_site.each_context(request),
            'object_name': object_name,
            'object': obj,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
            'is_popup': False,
            'title': "Are you sure?",
            'related_fileds': self.get_related_fields_data(obj),
            'is_popup': "_popup" in request.POST or "_popup" in request.GET,
            'to_field': to_field,
            **(extra_context or {}),
        }

        return TemplateResponse(
            request,
            "admin/datasets_delete_confirmation.html",
            context,
        )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
