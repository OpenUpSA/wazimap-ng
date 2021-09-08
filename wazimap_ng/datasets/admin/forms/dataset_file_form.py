from django import forms
from ... import models
from wazimap_ng.general.admin.forms import HistoryAdminForm

class DatasetFileAdminForm(HistoryAdminForm):

    class Meta:
        model = models.DatasetFile
        fields = '__all__'
