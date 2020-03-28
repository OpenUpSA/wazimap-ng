import uuid
import pathlib
import os

def get_random_filename(filename):
    ext = pathlib.Path(filename).suffix
    filename = os.path.join(uuid.uuid(), os.path.extsep, ext)
    return filename
