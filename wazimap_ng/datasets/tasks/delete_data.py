import logging
from typing import Dict

from django.db import transaction
from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)


@transaction.atomic
def delete_data(data: QuerySet, object_name: str, **kwargs) -> Dict:
    """
    Delete data
    """
    data.delete()

    is_queryset = isinstance(data, QuerySet)

    return {
        "is_queryset": is_queryset,
        "data": data,
        "object_name": object_name,
    }
