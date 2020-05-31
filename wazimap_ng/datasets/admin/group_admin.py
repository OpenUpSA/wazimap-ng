from django import forms
from django.contrib import admin

from .. import models
from .base_admin_model import DatasetBaseAdminModel

@admin.register(models.Group)
class GroupAdmin(DatasetBaseAdminModel):
    pass
    