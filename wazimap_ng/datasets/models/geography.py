from django.db import models
from django.contrib.postgres.indexes import GinIndex

from treebeard.mp_tree import MP_Node
from treebeard.ns_tree import NS_NodeManager, NS_NodeQuerySet

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import TrigramSimilarity


class GinTrgmIndex(GinIndex):
    """ GIN index from the pg_trgm extension.
    NOTE: before adding this index, be sure to have the `pg_trgm` extension installed.  This can be
    done by including (before any GinTrgmIndex indexs in model meta) the migration operation
    `django.contrib.postgres.operations.TrigramExtension`
    https://vxlabs.com/2018/01/31/creating-a-django-migration-for-a-gist-gin-index-with-a-special-index-operator/
    """

    def create_sql(self, model, schema_editor, using=''):
        """ This Statement is instantiated by the _create_index_sql() method of
        `django.db.backends.base.schema.BaseDatabaseSchemaEditor` using `sql_create_index` template,
        the original value being:
         "CREATE INDEX %(name)s ON %(table)s%(using)s (%(columns)s)%(extra)s"
        """
        statement = super().create_sql(model, schema_editor)
        statement.template =\
            "CREATE INDEX %(name)s ON %(table)s%(using)s (%(columns)s gin_trgm_ops)%(extra)s"
        return statement

class GeographyQuerySet(NS_NodeQuerySet):
    def search(self, text, similarity=0.3):
        return self.annotate(similarity=TrigramSimilarity("name", text)).filter(similarity__gt=similarity)

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



