from __future__ import annotations

from typing import Dict, List, Set

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import TrigramSimilarity
from django.db import models
from django.db.models.query import QuerySet
from treebeard.mp_tree import MP_Node, MP_NodeManager, MP_NodeQuerySet

from wazimap_ng.extensions.index import GinTrgmIndex
from wazimap_ng.general.models import BaseModel


class GeographyQuerySet(MP_NodeQuerySet):
    def search(self, text: str, similarity: float = 0.3) -> QuerySet:
        return (
            self
            .annotate(similarity=TrigramSimilarity("name", text))
            .filter(similarity__gt=similarity)
            .order_by("-similarity")
        )


class GeographyManager(MP_NodeManager):
    def get_queryset(self) -> GeographyQuerySet:
        return GeographyQuerySet(self.model, using=self._db)

    def search(self, text: str, similarity: float = 0.3) -> QuerySet:
        return self.get_queryset().search(text, similarity)


class Geography(MP_Node, BaseModel):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    level = models.CharField(max_length=20)
    version = models.CharField(max_length=20, blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.version})"

    objects = GeographyManager()

    class Meta:
        verbose_name_plural = "geographies"
        indexes = [
            GinTrgmIndex(fields=["name"]),
            models.Index(fields=["code"], name="idx_datasets_geography_code"),
        ]
        ordering = ["id"]

        constraints = [
            models.UniqueConstraint(fields=["version", "code"], name="unique_geography_code_version")
        ]

    def get_siblings(self) -> QuerySet:
        siblings = super(Geography, self).get_siblings()
        return siblings.filter(version=self.version)

    def get_child_boundaries(self) -> Dict[str, GeographyBoundary]:
        from ...boundaries.models import GeographyBoundary
        children: QuerySet = self.get_children()
        codes: List[str] = [c.code for c in children]
        levels: Set[str] = set(c.level for c in children)

        child_types: Dict[str, GeographyBoundary] = {}

        if len(children) > 0:
            for child_level in levels:
                child_types[child_level] = (
                    GeographyBoundary.objects
                    .filter(geography__code__in=codes, geography__level=child_level, geography__version=self.version)
                    .select_related("geography")
                )
        return child_types


class GeographyHierarchy(BaseModel):
    name = models.CharField(max_length=50)
    root_geography = models.ForeignKey(Geography, null=False, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    @property
    def version(self) -> str:
        return self.root_geography.version

    def help_text(self) -> str:
        return f"{self.name} : {self.description}"

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "Geography Hierarchies"
