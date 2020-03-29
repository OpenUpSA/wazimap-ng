import os
import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon

from wazimap_ng.datasets.models import Geography
from wazimap_ng.boundaries.models import GeographyBoundary

import fiona
from shapely.geometry import shape as shapely_shape

logger = logging.Logger(__name__)

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

    def process_root(self, fields, geo_shape):
        fields.pop("parent_code")
        area = fields.pop("area")
        g = Geography.add_root(**fields)
        fields.pop("level")
        GeographyBoundary.objects.create(geography=g, geom=geo_shape, area=area, **fields)

    def process_node(self, fields, geo_shape):
        parent_code = fields.pop("parent_code")
        area = fields.pop("area")

        try:
            parent_geography = Geography.objects.get(code__iexact=parent_code)
        except Geography.DoesNotExist:
            print(f"Can't find parent geography: {parent_code}")
            return

        try:
            geography = Geography.objects.get(code__iexact=fields["code"])
        except Geography.DoesNotExist:
            geography = parent_geography.add_child(code=fields["code"], level=fields["level"], name=fields["name"])
            fields.pop("level")
            GeographyBoundary.objects.create(geography=geography, geom=geo_shape, area=area, **fields)

    def extract_fields(self, field_map, properties):
        reverse_map = dict(zip(field_map.values(), field_map.keys()))

        code_field = reverse_map["code"]
        name_field = reverse_map["name"]
        parent_code_field = reverse_map["parent_code"]
        area_field = reverse_map["area"]

        return {
            "code": properties[code_field],
            "parent_code": properties[parent_code_field],
            "name": properties[name_field],
            "area": properties[area_field]
        }


    def process_shape(self, shape, field_map, level):
        properties = shape["properties"]

        fields = self.extract_fields(field_map, properties)
        fields["level"] = level

        if shape["geometry"] is None:
            print(f"No geometry present for {fields['code']}")
            return

        sh = shapely_shape(shape["geometry"])
        geometry = GEOSGeometry(sh.wkt)
        if type(geometry) == Polygon:
            geo_shape = MultiPolygon([geometry])
        else:
            geo_shape = geometry

        if fields["parent_code"] is None:
            process_as_root = input(f"""Geography '{fields["code"]}' does not have a parent. Load it as a root geography? (Y/N)?""")
            if not process_as_root.lower().startswith('n'):
                return self.process_root(fields, geo_shape)
            return
        else:
            self.process_node(fields, geo_shape)

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

