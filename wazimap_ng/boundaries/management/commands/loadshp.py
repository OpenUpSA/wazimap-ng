from django.utils.module_loading import import_string
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.utils import LayerMapping

app_label = "wazimap_ng.boundaries"
"""
Example process to load up shapefiles into the database

1. ./manage.py ogrinspect ./DC_SA_2011.shp District --mapping --multi >> wazimap_ng/boundaries/models.py
2. Edit the District model by moving the district_mapping into the model and changing the name to mapping. Change the field names as desired.
class District(models.Model):
    mapping = {
        'category': 'CATEGORY',
        'code': 'DC_MDB_C',
        'name': 'DC_NAME',
        'long_name': 'MAP_TITLE',
        'province_code': 'PR_MDB_C',
        'province_code': 'PR_CODE',
        'province': 'PR_NAME',
        'area': 'ALBERS_ARE',
        'geom': 'MULTIPOLYGON',
    }
    category = models.CharField(max_length=5)
    code = models.CharField(max_length=25)
    name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=200)
    province_code = models.CharField(max_length=50)
    pr_code_st = models.CharField(max_length=1)
    province = models.CharField(max_length=50)
    area = models.FloatField()
    geom = models.MultiPolygonField(srid=-1)

You'll probably need to edit the SRID on the geom column - e.g.
geom = models.MultiPolygonField(srid=4326)

3. ./manage.py makemigrations
4. ./manage.py migrate
5. ./manage loadshp District ./DC_SA_2011.shp
"""

class Command(BaseCommand):
    help = "Loads shapefiles into the database. Assume that the models already exist."

    def add_arguments(self, parser):
        parser.add_argument('model', type=str)
        parser.add_argument('shapefile', type=str)

    def handle(self, *args, **options):
        model_name = options["model"]
        filename = options["shapefile"]

        model = import_string(f"{app_label}.models.{model_name}")

        lm = LayerMapping(model, filename, model.mapping, transform=False, source_srs=4326)
        lm.save(strict=True, verbose=True)
