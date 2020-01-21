from django.db import models

from django.contrib.gis.db import models

def get_boundary_model_class(level):
    level = level.lower()
    model_classes = {
        "cy": Country, "country": Country,
        "pr": Province, "province": Province,
        "dc": District, "district": District,
        "mn": Municipality, "municipality": Municipality,
        "wd": Ward, "ward": Ward,
        "mp": Mainplace, "mainplace": Mainplace,
        "sp": Subplace, "Subplace": Subplace,
    }

    return model_classes.get(level, None)

class Country(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)

    area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326, null=True)

class Province(models.Model):
    mapping = {
        'code': 'PR_MDB_C',
        'name': 'PR_NAME',
        'area': 'ALBERS_ARE',
        'geom': 'MULTIPOLYGON',
    }

    code = models.CharField(max_length=5)
    name = models.CharField(max_length=25)
    area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)

class District(models.Model):
    mapping = {
        'category': 'CATEGORY',
        'code': 'DC_MDB_C',
        'name': 'DC_NAME',
        'long_name': 'MAP_TITLE',
        'province_code': 'PR_MDB_C',
        'province': 'PR_NAME',
        'area': 'ALBERS_ARE',
        'geom': 'MULTIPOLYGON',
    }
    category = models.CharField(max_length=5)
    code = models.CharField(max_length=25)
    name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=200)
    province_code = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return f"{self.province}: {self.name}"


class Municipality(models.Model):
    mapping = {
        'category_code': 'CATEGORY',
        'category': 'CAT2',
        'code': 'MN_MDB_C',
        'name': 'MN_NAME',
        'area': 'ALBERS_ARE',
        'geom': 'MULTIPOLYGON',
    }
    category_code = models.CharField(max_length=5)
    category = models.CharField(max_length=254)
    code = models.CharField(max_length=150)
    name = models.CharField(max_length=100)
    area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)


    def __str__(self):
        return f"{self.name} ({self.code})"


class Ward(models.Model):
    mapping = {
        'municipality_code': 'CAT_B',
        'code': 'WD_CODE_st',
        'area': 'ALBERS_ARE',
        'geom': 'MULTIPOLYGON',
    }
    municipality_code = models.CharField(max_length=25)
    code = models.CharField(max_length=8)
    area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return f"{self.municipality_code}: {self.wardno}"

class Mainplace(models.Model):
    mapping = {
        'code': 'MP_CODE_st',
        'name': 'MP_NAME',
        'municipality_code': 'MN_MDB_C',
        'municipality_name': 'MN_NAME',
        'area': 'ALBERS_ARE',
        'geom': 'MULTIPOLYGON',
    }

    code = models.CharField(max_length=6)
    name = models.CharField(max_length=254)
    municipality_code = models.CharField(max_length=7)
    municipality_name = models.CharField(max_length=254)
    area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)

def __str__(self):
    return f"{self.municipality_name}: {self.name}"


class Subplace(models.Model):
    mapping = {
        'code': 'SP_CODE_st',
        'name': 'SP_NAME',
        'mainplace_code': 'MP_CODE_st',
        'area': 'ALBERS_ARE',
        'geom': 'MULTIPOLYGON',
    }

    code = models.CharField(max_length=9)
    name = models.CharField(max_length=254)
    mainplace_code = models.CharField(max_length=6)
    area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return f"{self.mainplace_code}: {self.name}"

