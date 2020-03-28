import uuid
import pathlib
import os

def get_random_filename(filename):
    ext = pathlib.Path(filename).suffix
    filename = os.path.join(str(uuid.uuid4()), os.path.extsep, ext)
    return filename
