import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon

from wazimap_ng.datasets.models import Geography
from wazimap_ng.boundaries.models import GeographyBoundary

import fiona
from shapely.geometry import shape as shapely_shape

class Command(BaseCommand):
    help = "Loads new geographies. Example class: python3 manage.py loadshp /tmp/gcro.shp Region_cod=code,Parent_g_3=parent_code,Region_nam=name,Shape_Area=area planning_region"

    def add_arguments(self, parser):
        parser.add_argument("shapefile", type=str, help="Shapefile containing boundaries to be loaded.")
        parser.add_argument("field_map", type=str, help="Mapping of fields to extract from the shapefile. Should be formatted as follows: code_field=code,name_field=name,parent_code_field=parent_code,area_field=area....")
        parser.add_argument("level", type=str, help="Geography level, e.g. province, municipality, ...")

    def check_field_map(self, field_map):
        fields = ["name", "code", "parent_code", "area"]
        for f in fields:
            if f not in field_map.values():
                raise CommandError(f"Expected the following fields {fields}.")

    def check_shapefile(self, shapefile_path):
        if not os.path.exists(shapefile_path):
            raise CommandError(f"Can't find shapefile: {shapefile_path}")

    def process_shape(self, shape, field_map, level):
        reverse_map = dict(zip(field_map.values(), field_map.keys()))
        properties = shape["properties"]

        code_field = reverse_map["code"]
        name_field = reverse_map["name"]
        parent_code_field = reverse_map["parent_code"]

        code = properties[code_field]
        parent_code = properties[parent_code_field]
        name = properties[name_field]

        sh = shapely_shape(shape["geometry"])
        geo_shape = MultiPolygon([GEOSGeometry(sh.wkt)])

        try:
            parent_geography = Geography.objects.get(code__iexact=parent_code)
        except Geography.DoesNotExist:
            print(f"Can't find geography: {parent_code}")
            raise Geography.DoesNotExist()

        try:
            geography = Geography.objects.get(code__iexact=code)
        except Geography.DoesNotExist:
            geography = parent_geography.add_child(code=code, level=level, name=name)
            GeographyBoundary.objects.create(geography=geography, code=code, name=name, area=0, geom=geo_shape)

    @transaction.atomic()
    def handle(self, *args, **options):
        shapefile = options["shapefile"]
        field_map = dict(pair.split("=") for pair in options["field_map"].split(","))
        level = options["level"]

        self.check_shapefile(shapefile)
        self.check_field_map(field_map)

        shape = fiona.open(shapefile)
        for idx, s in enumerate(shape):
            self.process_shape(s, field_map, level)

        print(f"{idx + 1} geographies successfully loaded")

