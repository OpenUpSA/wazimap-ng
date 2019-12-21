from wazimap_ng.datasets import models
from django.db import transaction
import csv

cache = {}

def get_geo(prefix, parent, code, name, level):
    global cache
    key = "%s_%s" % (prefix, code)

    if key not in cache:
        new_geo = parent.add_child(code=code, name=name, level=level)
        cache[key] = new_geo

    return cache[key]

with transaction.atomic():
    models.Geography.objects.all().delete()
    south_africa = cache["root"] = models.Geography.add_root(name='South Africa', code="ZA")
    for idx, row in enumerate(csv.DictReader(open("subplaces.csv"))):
        print(row)
        province = get_geo("PR", parent=south_africa, code=row["PR_CODE"], name=row["PR_NAME"], level="province")
        district = get_geo("DC", parent=province, code=row["DC_MDB_C"], name=row["DC_NAME"], level="district")
        muni = get_geo("MN", parent=district, code=row["MN_MDB_C"], name=row["MN_NAME"], level="municipality")
        mp = get_geo("MP", parent=muni, code=row["MP_CODE"], name=row["MP_NAME"], level="mainplace")
        sp = get_geo("SP", parent=mp, code=row["SP_CODE"], name=row["SP_NAME"], level="subplace")

