import os

from django.db import models

from wazimap_ng import utils
from wazimap_ng.general.models import BaseModel


def get_file_path(instance, filename):
    filename = utils.get_random_filename(filename)
    return os.path.join('cms', filename)


class Page(BaseModel):
    profile = models.ForeignKey(
        'profile.Profile', on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=60)
    api_mapping = models.CharField(max_length=60)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Content(BaseModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    title = models.CharField(max_length=256, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(
    	upload_to=get_file_path, null=True, blank=True
    )
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]