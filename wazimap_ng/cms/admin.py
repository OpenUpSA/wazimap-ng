from django.contrib import admin

from . import models
# Register your models here.


@admin.register(models.Page)
class PageAdmin(admin.ModelAdmin):
	pass

@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
	pass