from django.db import models
from django.contrib.postgres.indexes import GinIndex
from tinymce.models import HTMLField
from django.contrib.postgres.fields import JSONField

from treebeard.mp_tree import MP_Node
from treebeard.mp_tree import MP_NodeManager, MP_NodeQuerySet

from django.contrib.postgres.search import TrigramSimilarity
from wazimap_ng.extensions.index import GinTrgmIndex
from wazimap_ng.general.models import BaseModel, SimpleHistory


class Version(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


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

class Geography(MP_Node, BaseModel):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    level = models.CharField(max_length=20)
    # versions = models.ManyToManyField(Version, blank=True)

    def __str__(self):
        hierarchies_str = ", ".join(h.name for h in self.get_root().geographyhierarchy_set.all())
        return f"{self.name} ({ hierarchies_str })"

    objects = GeographyManager()

    class Meta:
        verbose_name_plural = "geographies"
        indexes = [
            GinTrgmIndex(fields=["name"]),
            models.Index(fields=["code"], name="idx_datasets_geography_code"),
        ]
        ordering = ["id"]

    def get_version_siblings(self, version):
        siblings = super(Geography, self).get_siblings()
        siblings = siblings.filter(geographyboundary__version=version)
        return siblings

    def get_version_ancestors(self, version):
        ancestors = super(Geography, self).get_ancestors()
        ancestors = ancestors.filter(geographyboundary__version=version)
        return ancestors

    def get_child_boundaries(self, version):
        from ...boundaries.models import GeographyBoundary

        children = self.get_child_geographies(version)
        codes = [c.code for c in children]
        levels = set(c.level for c in children)

        child_types = {}

        if len(children) > 0:
            for child_level in levels:
                child_types[child_level] = (
                    GeographyBoundary.objects
                        .filter(
                            geography__code__in=codes,
                            geography__level=child_level,
                            version=version
                        )
                        .select_related("geography")
                )
        return child_types

    def get_child_geographies(self, version):
        child_geographies = self.get_children().filter(geographyboundary__version=version)
        return child_geographies

    @property
    def versions(self):
        return []
        return Version.objects.filter(geographyboundary__geography=self)


class GeographyHierarchy(BaseModel, SimpleHistory):
    name = models.CharField(max_length=50)
    root_geography = models.ForeignKey(Geography, null=False, on_delete=models.CASCADE, unique=True)
    description = HTMLField(blank=True)
    configuration = JSONField(default=dict, blank=True)

    @property
    def default_version(self):
        return self.configuration.get("default_version")

    def help_text(self):
        return f"{self.name} : {self.description}"


    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "Geography Hierarchies"
