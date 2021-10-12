import os
import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon

from wazimap_ng.datasets.models import Geography, GeographyHierarchy, Version
from wazimap_ng.boundaries.models import GeographyBoundary

import fiona
from shapely.geometry import shape as shapely_shape

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Loads new geographies. Example class: python3 manage.py loadshp /tmp/gcro.shp Region_cod=code,Parent_g_3=parent_code,Region_nam=name,Shape_Area=area planning_region"

    def add_arguments(self, parser):
        parser.add_argument("shapefile", type=str, help="Shapefile containing boundaries to be loaded.")
        parser.add_argument("field_map", type=str, help="Mapping of fields to extract from the shapefile. Should be formatted as follows: code_field=code,name_field=name,parent_code_field=parent_code,area_field=area....")
        parser.add_argument("hierarchy", type=str, help="Geography hierarchy name, e.g 'South Africa' or 'World'")
        parser.add_argument("level", type=str, help="Geography level, e.g. province, municipality, ...")
        parser.add_argument("version", type=str, help="Geography version, e.g. 'census 2016'...")
        parser.add_argument("--allow-root", action='store_true', help="Allow creating shape as root node without prompting")
        parser.add_argument("--create-hierarchy", action='store_true', help="Create the hierarchy if it doesn't exist without prompting")

    def check_field_map(self, field_map):
        fields = ["name", "code", "parent_code", "area"]
        for f in fields:
            if f not in field_map.values():
                raise CommandError(f"Expected the following fields {fields}.")

    def check_shapefile(self, shapefile_path):
        if not os.path.exists(shapefile_path):
            raise CommandError(f"Can't find shapefile: {shapefile_path}")

    def ensure_hierachy_exists(self, hierarchy_name, create_hierarchy, root_geography):
        try:
            return GeographyHierarchy.objects.get(name=hierarchy_name)
        except GeographyHierarchy.DoesNotExist:
            if not create_hierarchy:
                should_create = input(f"""Geography Hierarchy '{hierarchy_name}' not found. Create it? (Y/n)?""")
                if not should_create.lower().startswith('n'):
                    create_hierarchy = True
            if create_hierarchy:
                return GeographyHierarchy.objects.create(name=hierarchy_name, root_geography=root_geography)

    def process_root(self, fields, geo_shape, hierarchy_name, create_hierarchy, version):
        fields.pop("parent_code")
        area = fields.pop("area")

        try:
            g = Geography.objects.get(code=fields["code"], geographyhierarchy__name=hierarchy_name)
        except Geography.DoesNotExist:
            g = Geography.add_root(**fields)
            self.ensure_hierachy_exists(hierarchy_name, create_hierarchy, g)
        # g.versions.add(version)
        return GeographyBoundary.objects.create(geography=g, geom=geo_shape, area=area, version=version)

    def process_node(self, fields, geo_shape, hierarchy_name, version):
        parent_code = fields.pop("parent_code")
        area = fields.pop("area")

        try:
            hierarchy = GeographyHierarchy.objects.get(name=hierarchy_name)
        except GeographyHierarchy.DoesNotExist:
            print(f"Can't find hierarchy '{hierarchy_name}'. Ensure that exists by creating the root geography first.")
            return

        try:
            if hierarchy.root_geography.code.lower() == parent_code.lower() \
               and hierarchy.root_geography.geographyboundary_set.filter(version=version):
                parent_geography = hierarchy.root_geography
            else:
                parent_geography = hierarchy.root_geography.get_descendants().get(code__iexact=parent_code, geographyboundary__version=version)
        except Geography.DoesNotExist:
            parent_geography = None

        if parent_geography is None:
            print(f"Can't find parent geography: {parent_code} ({version}) in {hierarchy_name}")
            return

        try:
            geography = parent_geography.get_descendants().get(code__iexact=fields["code"])
        except Geography.DoesNotExist:
            geography = parent_geography.add_child(**fields)

        # geography.versions.add(version)
        if GeographyBoundary.objects.filter(geography=geography, version=version).count() == 0:
            GeographyBoundary.objects.create(geography=geography, geom=geo_shape, area=area, version=version)
        else:
            print(f"Not re-adding already-existing {version} boundary to {geography} in {hierarchy_name}")

        return True

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


    def process_shape(self, shape, field_map, allow_root, hierarchy_name, create_hierarchy, level, version):
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

        if fields["parent_code"] is None :
            if not allow_root:
                process_as_root = input(
                    f"""Geography '{fields["code"]}' does nothave a parent."""
                    """Load it as a root geography? (Y/n)?"""
                )
                if not process_as_root.lower().startswith('n'):
                    allow_root = True
            if allow_root:
                return self.process_root(fields, geo_shape, hierarchy_name, create_hierarchy, version)
            return
        else:
            return self.process_node(fields, geo_shape, hierarchy_name, version)

    @transaction.atomic()
    def handle(self, *args, **options):
        shapefile_path = options["shapefile"]
        field_map = dict(pair.split("=") for pair in options["field_map"].split(","))
        hierarchy_name = options["hierarchy"]
        level = options["level"]
        version_name = options["version"]
        create_hierarchy = options["create_hierarchy"]
        allow_root = options["allow_root"]
        version, created = Version.objects.get_or_create(name=version_name)

        self.check_shapefile(shapefile_path)
        self.check_field_map(field_map)

        shapefile = fiona.open(shapefile_path)
        for idx, shape in enumerate(shapefile):
            successful = self.process_shape(
                shape,
                field_map,
                allow_root,
                hierarchy_name,
                create_hierarchy,
                level,
                version
            )
            print(f"Loading shape {idx + 1} {'succeeded' if successful else 'failed'}")
