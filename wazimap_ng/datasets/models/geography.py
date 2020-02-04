from django.db import models
from django.contrib.postgres.indexes import GinIndex

from treebeard.mp_tree import MP_Node
from treebeard.mp_tree import MP_NodeManager, MP_NodeQuerySet

from django.contrib.postgres.search import TrigramSimilarity
from wazimap_ng.extensions.index import GinTrgmIndex


class GeographyQuerySet(MP_NodeQuerySet):
    def search(self, text, similarity=0.3):
        return (
            self
                .annotate(similarity=TrigramSimilarity("name", text))
                .filter(similarity__gt=similarity)
                .order_by("-similarity")
        )

class GeographyManager(MP_NodeManager):
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
            GinTrgmIndex(fields=["name"]),
            models.Index(fields=["code"], name="idx_datasets_geography_code"),
        ]
        ordering = ["id"]

    def get_child_boundaries(self):
        from ...boundaries.models import get_boundary_model_class
        children = self.get_children()
        codes = [c.code for c in children]
        levels = set(c.level for c in children)

        child_types = {}

        if len(children) > 0:
            for child_level in levels:
                boundary_class = get_boundary_model_class(child_level)
                if boundary_class is not None:
                    child_types[child_level] = boundary_class.objects.filter(code__in=codes).select_related("geography")
        return child_types



