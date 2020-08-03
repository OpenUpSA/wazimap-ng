from django.contrib.gis import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from django_q.tasks import async_task

from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.services.permissions import assign_perms_to_group
from wazimap_ng.general.admin import filters

from .. import models
from .forms import CategoryAdminForm
from wazimap_ng.datasets import hooks


@admin.register(models.Category)
class CategoryAdmin(BaseAdminModel):
    list_display = ("name",)
    form = CategoryAdminForm
    exclude = ("metadata", )

    fieldsets = (
        ("", {
            'fields': ('profile', 'name', "permission_type", )
        }),
        ("Import Collection", {
            'fields': ('import_collection', 'imported_collections')

        }),
        ("MetaData", {
          'fields': ('source', 'description', 'licence', )
        }),
    )
    list_filter = (filters.ThemeFilter,)
    readonly_fields = ("imported_collections", )
    search_fields = ("name", )

    class Media:
        css = {
             'all': ('/static/css/admin-custom.css',)
        }

    def imported_collections(self, obj):

        def get_url(file_obj):
            return '<a href="%s">%s</a>' % (reverse(
                'admin:%s_%s_change' % (
                    file_obj._meta.app_label, file_obj._meta.model_name
                ),  args=[file_obj.id]
            ), F"{file_obj.name}-{file_obj.id}")

        if obj:
            collection_file_links = [
                get_url(file_obj) for file_obj in models.CoordinateFile.objects.filter(
                    collection_id=obj.id, collection_id__isnull=False
                )
            ]
            if collection_file_links:
                return mark_safe(", ".join(collection_file_links))
        return "-"

    imported_collections.short_description = 'Previously Imported'

    def save_model(self, request, obj, form, change):
        is_new = obj.pk == None and change == False
        is_profile_updated = change and "profile" in form.changed_data

        super().save_model(request, obj, form, change)
        if is_new or is_profile_updated:
            assign_perms_to_group(obj.profile.name, obj, is_profile_updated)

        collection_import_file = form.cleaned_data.get("import_collection", None)

        if collection_import_file:
            collection_obj = models.CoordinateFile.objects.create(
                name=obj.name,
                document=collection_import_file,
                collection_id=obj.id
            )
            task = async_task(
                "wazimap_ng.points.tasks.process_uploaded_file",
                collection_obj, obj,
                task_name=f"Uploading data: {obj}",
                hook="wazimap_ng.datasets.hooks.process_task_info",
                key=request.session.session_key,
                type="upload", assign=True, notify=True
            )
            hooks.add_to_task_list(request.session, task)
            hooks.custom_admin_notification(
                request.session,
                "info",
                "Data upload for %s started. We will let you know when process is done." % (
                    obj.name
                )
            )
        return obj
