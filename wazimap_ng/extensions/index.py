from django.contrib.postgres.indexes import GinIndex

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
