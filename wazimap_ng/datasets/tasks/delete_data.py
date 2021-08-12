import logging

from django.db import transaction
from django.db.models.query import QuerySet
from django.conf import settings

logger = logging.getLogger(__name__)


@transaction.atomic
def delete_data(data, object_name, **kwargs):
    """
    Delete data
    """
    str_of_objs = [str(x) for x in data]
    data.delete()

    is_queryset = isinstance(data, QuerySet)

    return {
        "is_queryset": is_queryset,
        "data": str_of_objs,
        "object_name": object_name,
    }
