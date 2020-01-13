from django.db import models
from django.contrib.postgres.indexes import GinIndex

from treebeard.mp_tree import MP_Node
from treebeard.ns_tree import NS_NodeManager, NS_NodeQuerySet

from django.contrib.postgres.search import TrigramSimilarity
from wazimap_ng.extensions.index import GinTrgmIndex

class GeographyQuerySet(NS_NodeQuerySet):
    def search(self, text, similarity=0.3):
        return self.annotate(similarity=TrigramSimilarity("name", text)).filter(similarity__gt=similarity).order_by("-similarity")

class GeographyManager(NS_NodeManager):
    def get_queryset(self):
        return GeographyQuerySet(self.model, using=self._db)

    def search(self, text, similarity=0.3):
        return self.get_queryset().search(text, similarity)

class Geography(MP_Node):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    level = models.CharField(max_length=20)

    def __str__(self):
        return "%s" % self.name

    objects = GeographyManager()

    class Meta:
        verbose_name_plural = "geographies"
        indexes = [
            GinTrgmIndex(fields=["name"])
        ]
        ordering = ["id"]



