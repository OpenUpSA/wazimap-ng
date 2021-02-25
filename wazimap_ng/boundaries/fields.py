# usage:

# from django.contrib.gis.db import models
# from fields import CachedMultiPolygonField
#
#
# class MyGeography(models.model):
#     name = models.CharField(max_length=128)
#     geom = models.MultiPolygonField(srid=4326, null=True, blank=True)
#     geom_cache = CachedMultiPolygonField(field_name='geom', simplify=0.0002, precision=4)
#

# and when your MyGeography object gets saved, its simplified / smaller counterpart will be available at `my_geography_object.geom_cache`


from django.contrib.gis.db.models.fields import MultiPolygonField
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, WKTWriter


class CachedMultiPolygonField(MultiPolygonField):

    def __init__(self, **kwargs):

        self.simplify = kwargs.pop('simplify', 0.002)
        self.precision = kwargs.pop('precision', 4)
        self.field_name = kwargs.pop('field_name', None)

        kwargs['null'] = True
        kwargs['blank'] = True

        return super(CachedMultiPolygonField, self).__init__(**kwargs)

    def pre_save(self, model_instance, add):

        if not getattr(model_instance, self.attname):

            try:
                wkt_writer = WKTWriter(precision=self.precision)
                value = GEOSGeometry(wkt_writer.write(getattr(model_instance, self.field_name).simplify(self.simplify, preserve_topology=True)))
                if not isinstance(value, MultiPolygon):
                    value = MultiPolygon(value)
                setattr(model_instance, self.attname, value)
                return value
            except:
                pass

        return super(CachedMultiPolygonField, self).pre_save(model_instance, add)
