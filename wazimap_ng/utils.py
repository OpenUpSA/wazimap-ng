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

def mergedict(a, b, path=None, concatenate_arrays=True, update=True):
    """
    Derived from: http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge
    merges b into a

        concatenate_arrays - if True then arrays are concatenate, otherwise they are recursively traversed
        update - if True then values in b clobber values in a
    """
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                mergedict(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                if concatenate_arrays:
                    a[key].extend(b[key])
                else:
                    for idx, val in enumerate(b[key]):
                        a[key][idx] = mergedict(a[key][idx], b[key][idx], path + [str(key), str(idx)], update=update)
            elif update:
                a[key] = b[key]
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]

def qsdict(qs, *args):
    """
    Convert a query string to a nested dict
    :param qs: The query string from which the array will be created. qs can also be an object and args are all attributes on that object.
    :param args: A list of fields which will be nested one inside the other in the dict. The last arg will be the value in the innermost dict. If an arg is callable then it will be executed with q as a parameter. If the last parameter is a tuple then all the values inside that tuple will be added as leaves.
    :return:  A nested dict

    e.g.
    qs = Queryset([{fa:1, fb:2, fc:3}, {fa:3, fb:4, fc:5}]),
    using fc as the value

    {
        1 : {
            2 : 3
        },
        3 : {
            4 : 5
        }
    }
    """

    if len(args) < 2:
        raise ValueError("Need at least two fields to nest dicts")

    args = list(args)

    def v(q, key):
        if callable(key):
            return key(q)
        elif hasattr(q, key):
            return getattr(q, key)
        elif key in q:
            return q[key]
        else:
            return None

    d = {}
    for q in qs:
        nested_dicts = [d]
        for idx, key in enumerate(args[:-2]):
            current_dict = nested_dicts[-1]
            value = v(q, key)
            if type(value) == list:
                arr = value
                for el in arr:
                    current_dict[el] = qsdict([q], *args[idx + 1:])
                break
            else:
                if not value in current_dict:
                    current_dict[value] = OrderedDict()
                nested_dicts.append(current_dict[value])
        else:
            current_dict = nested_dicts[-1]
            value = v(q, args[-2])
            if type(value) == list:
                arr = value
                for el in arr:
                    current_dict[el] = v(q, args[-1]) # need to handle a tuple as well
                
            else:
                if type(args[-1]) == tuple:
                    current_dict[v(q, args[-2])] = [v(q, el) for el in args[-1]]
                else:
                    current_dict[v(q, args[-2])] = v(q, args[-1])

    return d

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

# Tests
def test_qdict_empty_input():
    if not pytest_available:
        return

    with pytest.raises(ValueError):
        d = qsdict([])

    with pytest.raises(ValueError):
        d = qsdict([[]])

def test_qdict_empty_row():
    if not pytest_available:
        return

def test_qdict_at_least_two_parameters():
    if not pytest_available:
        return

    with pytest.raises(ValueError):
        d = qsdict([{"a": "b"}], "a")

def test_qdict_basic_input():
    d = qsdict([{"a": "b", "c": "d"}], "a", "c")
    assert d == {
        "b": "d"
    }



def test_qdict_two_rows():
    d = qsdict([
        {"a": "b", "c": "d"},
        {"a": "c", "c": "e"},
    ], "a", "c")

    assert d == {
        "b": "d",
        "c": "e"
    }

def test_qdict_overwrites_value_with_two_parameters():
    d = qsdict([
        {"a": "b", "c": "d"},
        {"a": "b", "c": "f"},
    ], "a", "c")

    assert d == {
        "b": "f"
    }

def test_qdict_3_level_nesting():
    d = [
        {"a": 1, "b": 2, "c": 3},
        {"a": 1, "b": 4, "c": 6},
    ]

    d1 = qsdict(d, "a", "b", "c")

    assert d1 == {
        1 : {
            2: 3,
            4: 6
        }
    }

    d2 = qsdict(d, "b", "a", "c")

    assert d2 == {
        2 : {
            1: 3
        },
        4 : {
            1: 6
        }
    }

def test_callable():
    d = [
        {"a": 1, "b": 2, "c": 3},
        {"a": 1, "b": 4, "c": 6},
    ]

    d1 = qsdict(d, "a", lambda x: "Hello World", "b", "c")

    assert d1 == {
        1 : {
            "Hello World": {
                2: 3,
                4: 6
            }
        }
    }

    d2 = qsdict(d, "b", lambda x: x["a"] + 1,  "c")

    assert d2 == {
        2 : {
            2: 3
        },
        4 : {
            2: 6
        }
    }

def test_object_properties():
    class TestClass:
        def __init__(self, a, b, c):
            self.a, self.b, self.c = a, b, c

    c1 = TestClass(1, 2, 3)
    c2 = TestClass(1, 4, 6)

    d = [c1, c2]

    d1 = qsdict(d, "a", "b", "c")

    assert d1 == {
        1 : {
            2: 3,
            4: 6
        }
    }

def test_long_input():
    d = [
        {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
        {"a": 1, "b": 2, "c": 3, "d": 7, "e": 8},
    ]

    d1 = qsdict(d, "a", "b", "c", "d",  "e")

    assert d1 == {
        1: {
            2: {
                3: {
                    4: 5,
                    7: 8
                } 
            }
        }
    }

def test_array():
    d = [
        {"a": 1, "b": ["x", "y"], "c": 4, "d": 5},
        {"a": 2, "b": ["x", "y"], "c": 4, "d": 6}
    ]


    d1 = qsdict(d, "a", "b", "c", "d")

    assert d1 == {
        1: {
            "x": {
                4: 5
            },
            "y": {
                4: 5
            }
        },
        2: {
            "x": {
                4: 6
            },
            "y": {
                4: 6
            }
        }
    }

def test_multiple_arrays():
    d = [
        {"a": 1, "b": ["x", "y"], "c": 2, "d": ["z", "w"], "e": 5, "f": 6},
        {"a": 2, "b": ["x", "y"], "c": 4, "d": ["z", "w"], "e": 6, "f": 8}
    ]


    d1 = qsdict(d, "a", "b", "c", "d", "e", "f")

    assert d1 == {
        1: {
            "x": {
                2: {
                    "z": {
                        5: 6
                    },
                    "w": {
                        5: 6
                    }
                }
            },
            "y": {
                2: {
                    "z": {
                        5: 6
                    },
                    "w": {
                        5: 6
                    }
                }
            }
        },
        2: {
            "x": {
                4: {
                    "z": {
                        6: 8
                    },
                    "w": {
                        6: 8
                    }
                }
            },
            "y": {
                4: {
                    "z": {
                        6: 8
                    },
                    "w": {
                        6: 8
                    }
                }
            }
        }
    }

def test_array_at_the_end():
    d = [
        {"a": 1, "b": 3, "c": 5, "d": ["x", "y"]},
        {"a": 2, "b": 4, "c": 6, "d": ["x", "y"]},
    ]


    d1 = qsdict(d, "a", "b", "c", "d")

    assert d1 == {
        1: {
            3: {
                5: ["x", "y"]
            }
        },
        2: {
            4: {
                6: ["x", "y"]
            }
        }
    }

def test_array_at_second_last_position():
    d = [
        {"a": 1, "b": 3, "c": ["x", "y"], "d": 5},
        {"a": 2, "b": 4, "c": ["x", "y"], "d": 6},
    ]


    d1 = qsdict(d, "a", "b", "c", "d")

    assert d1 == {
        1: {
            3: {
                "x": 5,
                "y": 5 
            }
        },
        2: {
            4: {
                "x": 6,
                "y": 6 
            }
        },
    }


def flatten_dict(d):
    """
    Flatten a dictionary into an array of arrays e.g:

    {
        a: {
            x: 2,
            y: 3
        },
        b: {
            x: 4,
            y: 5
        }
    }

    becomes
    [
        [a, x, 2],
        [a, y, 3],
        [b, x, 4],
        [b, y, 5],
    ]

    used as a component of the pivot function
    
    """
    if not isinstance(d, Mapping):
        return [[d]]

    arr = []
    for k, v in d.items():
        for el in flatten_dict(v):
            arr.append([k] + el)

    return arr

def rearrange(in_arrs, order):
    """
    rearrange elements in a given list of arrays. The last element always remains in place

    e.g.
    d =[
        [a, x, 2],
        [a, y, 3],
        [b, x, 4],
        [b, y, 5],
    ]

    rearrange(d, [1, 0])

    d =[
        [x, a, 2],
        [y, a, 3],
        [x, b, 4],
        [y, b, 5],
    ]

    used as a componenbt of the pivot function
    """
    out_arrs = []
    for arr in in_arrs:
        out_arrs += [[arr[idx] for idx in order if arr[idx] != arr[-1]] + [arr[-1]]]

    return out_arrs

def nest(arrays, root=None):
    """
    Unflatten a dictionary. Similar to qsdict but is simpler and works on arrays
    """
    if len(arrays) == 0:
        return {}


    d = root or defaultdict(dict)
    for arr in arrays:
        if len(arr) >= 2:
            head, *tail = arr
            if len(tail) == 1:
                d[head] = tail[0]
            elif len(tail) > 1:
                d[head] = nest([tail], d[head])
    return d
        
def pivot(d, order):
    """
    Pivots an array by a list of keys

    d = {
        "A": {
            "Category1": {
                "X": 111111,
                "Y": 222222,
            },
            "Category2": {
                "X": 333333,
                "Y": 444444,
            },
            "Category3": {
                "X": 555555,
                "Y": 666666,
            }
        },
        "B": {
            "Category1": {
                "X": 777777,
                "Y": 888888,
            },
            "Category2": {
                "X": 999999,
                "Y": 101010,
            },
            "Category3": {
                "X": 101011,
                "Y": 101012,
            }
        },
    }

    pivot(d, [2, 1, 0]) 

    becomes:
    
    d = {
    "X": {
        "Category1": {
            "A": 111111,
            "B": 777777,
        },
        "Category2": {
            "A": 333333,
            "B": 999999,
        },
        "Category3": {
            "A": 555555,
            "B": 101011,
        },
    },
    "Y": {
        "Category1": {
            "A": 222222,
            "B": 888888,
        },
        "Category2": {
            "A": 444444,
            "B": 101010,
        },
        "Category3": {
            "A": 666666,
            "B": 101012,
        },
    },
}
    """
    flattened = flatten_dict(d)
    rearranged = rearrange(flattened, order)
    nested = nest(rearranged)

    return nested