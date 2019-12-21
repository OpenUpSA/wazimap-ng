from django.db import models
from treebeard.mp_tree import MP_Node

class Geography(MP_Node):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    level = models.CharField(max_length=20)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = "geographies"



