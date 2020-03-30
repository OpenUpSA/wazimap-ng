from django.contrib.gis import admin
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres import fields
from django.contrib import  messages
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from django_q.tasks import async_task
from django_q.models import Task
from wazimap_ng.datasets import hooks
from django.urls import reverse
from django.conf import settings
from django import forms
import pandas as pd

from . import models

admin.site.register(models.Theme)

def assign_to_category_action(category):
    def assign_to_category(modeladmin, request, queryset):
        queryset.update(category=category)
        messages.info(request, "Locations assigned to category {0}".format(category.name))

    assign_to_category.short_description = "Assign to {0}".format(category.name)
    assign_to_category.__name__ = 'assign_to_category_{0}'.format(category.id)

    return assign_to_category

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "theme",)
    list_filter = ("theme",)

@admin.register(models.Location)
class LocationAdmin(admin.OSMGeoAdmin):
    formfield_overrides = {
        fields.JSONField: {"widget": JSONEditorWidget},
      }

    list_display = ("name", "category",)
    list_filter = ("category",)

    def get_actions(self, request):
        actions = super().get_actions(request)

        for category in models.Category.objects.all():
            action = assign_to_category_action(category)
            actions[action.__name__] = (
                action, action.__name__, action.short_description
            )

        return actions

class InitialDataUploadChangeView(admin.StackedInline):
    model = models.CoordinateFile
    fk_name = "profile_category"
    exclude = ("task", )
    can_delete = False
    verbose_name = ""
    verbose_name_plural = ""

    fieldsets = (
        ("Uploaded Collection Data", {
            "fields": ("document", )
        }),
        ("Task Details", {
            "fields": ("get_status", "get_task_link",)
        }),
    )

    error_and_warning_fildset = ("Error while data extraction", {
        "fields": ("get_errors",)
    })

    readonly_fields = (
        "document", "get_status", "get_task_link", "get_errors",
    )

    def get_status(self, obj):
        if obj.id:
            if obj.task:
                return "Processed" if obj.task.success else "Failed"
            return "In Queue"

    get_status.short_description = 'Status'

    def get_task_link(self, obj):
        if obj.task:
            task_type = "success" if obj.task.success else "failure"
            admin_url = reverse(
                'admin:%s_%s_change' % (
                    obj.task._meta.app_label, task_type
                ),  args=[obj.task.id]
            )

            return mark_safe('<a href="%s">%s</a>' % (admin_url, obj.task.id))
        return "-"

    get_task_link.short_description = 'Task Link'

    def get_errors(self, obj):
        if obj.task and not obj.task.success:
            result = obj.task.result
            if "CustomDataParsingExecption" in result:
                logdir = settings.MEDIA_ROOT + "/logs/points/"
                filename = "%s_%d_log.csv" % ("point_file", obj.id)
                download_url = settings.MEDIA_URL + "logs/points/"

                df = pd.read_csv(logdir+filename, header=None, sep=",", nrows=10, skiprows=1)
                error_list = df.values.tolist()

                result = render_to_string(
                    'custom/render_task_errors.html', { 'errors': error_list, 'download_url': download_url+filename}
                )

            return mark_safe(result)
        return "None"

    get_errors.short_description = 'Errors'

    def get_fieldsets(self, request, obj):
        fields = super().get_fieldsets(request, obj)
        if obj.coordinatefile.task:
            fields = fields + (self.error_and_warning_fildset, )

        return fields


class InitialDataUploadAddView(admin.StackedInline):
    model = models.CoordinateFile
    fk_name = "profile_category"
    exclude = ("task", )
    can_delete = False
    verbose_name = ""
    verbose_name_plural = ""

    fieldsets = (
        ("Initial Data Upload - Use this form to upload file that will allow us to create points.", {
            "fields": ("document",)
        }),
    )


class PointsCollectionAdminForm(forms.ModelForm):
    theme = forms.ModelChoiceField(queryset=models.Theme.objects.all(), required=True)
    subtheme = forms.CharField(required=True)
    class Meta:
        model = models.ProfileCategory
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['theme'].required = False
            self.fields['subtheme'].required = False


@admin.register(models.ProfileCategory)
class ProfileCategoryAdmin(admin.ModelAdmin):
    list_display = ("label", "category", "profile")
    list_filter = ("category", "profile",)
    form = PointsCollectionAdminForm

    fieldsets_add_view = (
        ("Database fields (can't change after being created)", {
            'fields': ('profile', 'theme', 'subtheme')
        }),
        ("Point Collection description fields", {
          'fields': ('label', 'description',)
        }),
    )

    fieldsets_change_view = (
        ("Database fields", {
            'fields': ('profile', 'category')
        }),
        ("Point Collection description fields", {
          'fields': ('label', 'description',)
        }),
    )
    inlines = ()

    class Media:
        css = {
             'all': ('/static/css/admin-custom.css',)
        }

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile", "category", ) + self.readonly_fields
        return self.readonly_fields

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = (InitialDataUploadAddView, )
        self.fieldsets = self.fieldsets_add_view
        return super().add_view(request)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = (InitialDataUploadChangeView, )
        self.fieldsets = self.fieldsets_change_view
        return super().change_view(request, object_id)

    def save_model(self, request, obj, form, change):
        if obj.pk == None and change == False:
            subtheme = models.Category.objects.create(
                theme=form.cleaned_data["theme"],
                name=form.cleaned_data["subtheme"]
            )
            obj.category = subtheme

        return super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        if formset.model == models.CoordinateFile:
            instances = formset.save()
            for instance in instances:
                async_task(
                    "wazimap_ng.points.tasks.process_uploaded_file",
                    instance, 
                    task_name=f"Uploading data: {instance}",
                    hook="wazimap_ng.datasets.hooks.process_task_info",
                    key=request.session.session_key,
                    type="upload", assign=True, notify=True
                )

                hooks.custom_admin_notification(
                    request.session,
                    "info",
                    "Data upload for %s started. We will let you know when process is done." % (
                        instance
                    )
                )
