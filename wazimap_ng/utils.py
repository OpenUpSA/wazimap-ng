import uuid
import pathlib
import os

def get_random_filename(filename):
    ext = pathlib.Path(filename).suffix
    filename = os.path.join(str(uuid.uuid4()), os.path.extsep, ext)
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
