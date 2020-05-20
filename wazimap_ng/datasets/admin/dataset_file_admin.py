from .. import models
from .base_admin_model import BaseAdminModel
from django.contrib import admin

@admin.register(models.DatasetFile)
class DatasetFileAdmin(BaseAdminModel):
	pass