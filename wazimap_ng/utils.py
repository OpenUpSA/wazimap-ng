import uuid
import pathlib
import os
from collections import OrderedDict, defaultdict, Mapping
import logging

logger = logging.getLogger(__name__)

def get_random_filename(filename):
    filename = f"{uuid.uuid4()}_{filename}"
    return filename

def truthy(s):
    if noney(s): return None

    return str(s).lower() == "true" or str(s) == 1

def noney(n):
    return n is None or str(n).lower() == "none"

def int_or_none(i):
    if noney(i):
        return None

    return int(i) 

def sort_list_using_order(lst, order, key_func=lambda x: x):
    if len(lst) == 0:
        return []

    if order is None or len(order) == 0:
        return lst

    lookup = {o: idx for idx, o in enumerate(order)}
    infinity = float("inf")
    return sorted(lst, key=lambda x: lookup.get(key_func(x), infinity))


def expand_nested_list(lst, key):
    """
    [{"a": "b", key: [1, 2, 3]}]

    becomes
    [
        {"a": "b", key: 1},
        {"a": "b", key: 2},
        {"a": "b", key: 3}
    ]
    """
    for row in lst:
        for js in row[key]:
            row_copy = row.copy()
            row_copy[key] = js
            yield row_copy

try:
    pytest_available = True
    import pytest
except ImportError as error:
    pytest_available = False
    logger.warning("pytest not installed - some tests cannot be run.")
