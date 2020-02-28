import operator
from functools import reduce

from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.postgres import fields
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from django_json_widget.widgets import JSONEditorWidget
from django import forms
from django.db.models import Q, CharField
from django.db.models.functions import Cast
from django.template.response import TemplateResponse
from django.contrib.admin.utils import model_ngettext, unquote
from django.core.exceptions import PermissionDenied

from django_q.tasks import async_task

from . import models
from . import widgets
from . import hooks

admin.site.register(models.IndicatorCategory)
admin.site.register(models.IndicatorSubcategory)
admin.site.register(models.Profile)

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

            async_task(
                'wazimap_ng.datasets.tasks.delete_data',
                queryset, objects_name,
                task_name=f"Deleting data: {objects_name}",
                hook="wazimap_ng.datasets.hooks.notify_user",
                key=request.session.session_key,
                type="delete"
            )
            modeladmin.delete_queryset(request, queryset)
            modeladmin.message_user(request, "Successfully deleted %(count)d %(items)s." % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            }, messages.SUCCESS)
        # Return None to display the change list page again.
        return None

    related_fileds_data = {}

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
    hooks.custom_admin_notification(
        request.session,
        "info",
        "We run data deletion in background because of related data and caches. We will let you know when processing is done"
    )
    return TemplateResponse(
        request,
        "admin/datasets_delete_selected_confirmation.html",
        context,
    )


delete_selected_data.short_description = "Delete selected objects"

class BaseAdminModel(admin.ModelAdmin):

    actions = [delete_selected_data]

    def get_related_fields_data(self, obj):
        return []

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
            async_task(
                'wazimap_ng.datasets.tasks.delete_data',
                obj, object_name,
                task_name=f"Deleting data: {obj.name}",
                hook="wazimap_ng.datasets.hooks.notify_user",
                key=request.session.session_key,
                type="delete"
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

        hooks.custom_admin_notification(
            request.session,
            "info",
            "We run data deletion in background because of related data and caches. We will let you know when processing is done"
        )
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

def customTitledFilter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper

@admin.register(models.Dataset)
class DatasetAdmin(BaseAdminModel):
    readonly_fields = ("groups",)

    def get_related_fields_data(self, obj):

        return [{
                "name": "dataset data",
                "count": obj.datasetdata_set.count()
            }, {
                "name": "indicator",
                "count": obj.indicator_set.count()
        }]

@admin.register(models.Geography)
class GeographyAdmin(TreeAdmin):
    form = movenodeform_factory(models.Geography)
    list_display = (
        "name", "code", "level"
    )

    list_filter = ("level",)


def description(description, func):
    func.short_description = description
    return func


@admin.register(models.ProfileIndicator)
class ProfileIndicatorAdmin(admin.ModelAdmin):
    list_filter = (
        ('profile__name', customTitledFilter('Profile')),
        ('indicator__name', customTitledFilter('Indicator')),
        ('subcategory__category__name', customTitledFilter('Category')),
        "subcategory",
    )

    list_display = (
        "profile",
        "label", 
        description("Indicator", lambda x: x.indicator.name), 
        description("Category", lambda x: x.subcategory.category.name),
        "subcategory",
        "key_metric",
    )

    fieldsets = (
        ("Database fields (can't change after being created)", {
            'fields': ('profile', 'indicator')
        }),
        ("Profile fields", {
          'fields': ('label', 'subcategory', 'key_metric', 'description')
        }),
        ("Subindicators", {
          'fields': ('subindicators',)
        })
    )

    formfield_overrides = {
        fields.ArrayField: {"widget": widgets.SortableWidget},
    }

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile",) + self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.subindicators = obj.indicator.subindicators
        super().save_model(request, obj, form, change)

@admin.register(models.ProfileHighlight)
class ProfileHighlightAdmin(admin.ModelAdmin):
    list_filter = (
        ("profile__name", customTitledFilter("Profile")),
        ("indicator__name", customTitledFilter("Indicator")),
    )

    list_display = (
        "profile", 
        "name", 
        "label", 
        description("Indicator", lambda x: x.indicator.name), 
    )

    fieldsets = (
        ("Database fields (can't change after being created)", {
            "fields": ("profile", "name", "indicator")
        }),
        ("Profile fields", {
          "fields": ("label", "value")
        })
    )

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile", "name") + self.readonly_fields
        return self.readonly_fields

class IndicatorAdminForm(forms.ModelForm):
    groups = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = models.Indicator
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            choices = [[group, group] for group in self.instance.dataset.groups]

            if "groups" in self.fields:
                self.fields['groups'].choices = choices
                self.fields['groups'].initial = self.instance.groups

            if "universe" in self.fields:
                if not self.instance.dataset.groups:
                    self.fields['universe'].queryset = models.Universe.objects.none()
                else:
                    condition = reduce(
                        operator.or_, [Q(as_string__icontains=group) for group in self.instance.dataset.groups]
                    )
                    self.fields['universe'].queryset = models.Universe.objects.annotate(
                        as_string=Cast('filters', CharField())
                    ).filter(condition)

@admin.register(models.Indicator)
class IndicatorAdmin(BaseAdminModel):

    list_display = (
        "name", "dataset", "universe"
    )

    list_filter = (
        ("dataset", customTitledFilter("Dataset")),
    )

    form = IndicatorAdminForm
    fieldsets_add_view = [
        (None, { 'fields': ('dataset', ) } ),
    ]
    fieldsets = [
        (None, { 'fields': ('dataset','universe', 'groups', 'name', 'subindicators') } ),
    ]

    formfield_overrides = {
        fields.ArrayField: {"widget": widgets.SortableWidget},
    }

    def get_related_fields_data(self, obj):
        return [{
            "name": "indicator data",
            "count": obj.indicatordata_set.count()
        }]

    def add_view(self, request, form_url='', extra_context=None):
        if request.POST.get("_saveasnew"):
            self.fieldsets = IndicatorAdmin.fieldsets
        else:
            self.fieldsets = IndicatorAdmin.fieldsets_add_view

        extra_context = extra_context or {}
        extra_context['show_save'] = False
        return admin.ModelAdmin.add_view(self, request, form_url, extra_context)

    def change_view(self, request, *args, **kwargs):
        self.fieldsets = IndicatorAdmin.fieldsets
        return admin.ModelAdmin.change_view(self, request, *args, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            to_add = ('dataset',)
            if obj.name:
                to_add = to_add + ("groups", "universe",)
            return self.readonly_fields + to_add
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        run_task = False

        if change:
            db_obj = models.Indicator.objects.get(id=obj.id)
            if not db_obj.name:
                run_task = True
        super().save_model(request, obj, form, change)
        if run_task:
            async_task(
                "wazimap_ng.datasets.tasks.indicator_data_extraction",
                obj,
                task_name=f"Data Extraction: {obj.name}",
                hook="wazimap_ng.datasets.hooks.notify_user",
                key=request.session.session_key
            )
            hooks.custom_admin_notification(
                request.session,
                "info",
                "Process of Data extraction started for %s. We will let you know when process is done." % (
                    obj.name
                )
            )

        if not change:
            hooks.custom_admin_notification(
                request.session,
                "warning",
                "Please make sure you get data right before saving as fields : groups, dataset & universe will be set as non editable"
            )
        return obj

@admin.register(models.Universe)
class UniverseAdmin(admin.ModelAdmin):
  formfield_overrides = {
    fields.JSONField: {"widget": JSONEditorWidget},
  }

@admin.register(models.DatasetFile)
class DatasetFileAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        is_created = obj.pk == None and change == False
        super().save_model(request, obj, form, change)
        if is_created:
            async_task(
                "wazimap_ng.datasets.tasks.process_uploaded_file",
                obj, task_name=f"Uploading data: {obj.title}",
                hook="wazimap_ng.datasets.hooks.notify_user",
                key=request.session.session_key
            )
            hooks.custom_admin_notification(
                request.session,
                "info",
                "Data upload for %s started. We will let you know when process is done." % (
                    obj.title
                )
            )
        return obj

@admin.register(models.IndicatorData)
class IndicatorDataAdmin(admin.ModelAdmin):

    def indicator__name(self, obj):
        return obj.indicator.name

    def parent(self, obj):
        return obj.geography.get_parent()

    formfield_overrides = {
        fields.JSONField: {"widget": JSONEditorWidget},
    }

    fieldsets = (
        ("Database fields (can't change after being created)", {
            "fields": ("geography", "indicator")
        }),
        ("Data fields", {
          "fields": ("data",)
        })
    )

    list_display = (
        "indicator__name", "geography", "parent"
    )

    list_filter = ("indicator__name",)

    search_fields = ["geography__name"]

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("geography", "indicator") + self.readonly_fields
        return self.readonly_fields