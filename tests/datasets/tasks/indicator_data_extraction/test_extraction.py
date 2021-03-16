import pytest

from wazimap_ng.datasets.models import IndicatorData, Geography
from wazimap_ng.datasets.tasks.indicator_data_extraction import indicator_data_extraction

from tests.datasets.factories import (
    DatasetFactory,
    DatasetDataFactory,
    GeographyFactory,
    GeographyHierarchyFactory,
    IndicatorFactory,
    DatasetFileFactory
)
      
@pytest.fixture
def datasetdata2(datasetdata, geographies):
    gendict = lambda d, g: {**d.data, **{"geography": g.pk}}
    dataset = datasetdata[0].dataset
    new_geographies = geographies[1:]
    new_datasetdata = [
        DatasetDataFactory(dataset=dataset, geography=g, data=gendict(d, g))
        for g in new_geographies
        for d in datasetdata
    ]

    datasetdata

    return datasetdata + new_datasetdata

@pytest.mark.django_db
class TestIndicatorDataExtraction:
    def test_basic_extraction(self, datasetdata, indicator, geographies):
        no_data = lambda x: len(x.data) == 0
        geography = geographies[0]

        assert IndicatorData.objects.count() == 0

        indicator_data_items = indicator_data_extraction(indicator)
        assert len(indicator_data_items) == 1
        assert IndicatorData.objects.count() == 1


        assert all(no_data(idata) for idata in IndicatorData.objects.exclude(geography=geography))

        indicator_data = IndicatorData.objects.get(geography=geography)
            
        assert indicator_data.data == [
            {"gender": "male", "age": "15", "language": "isiXhosa", "count": 1},
            {"gender": "male", "age": "15", "language": "isiZulu", "count": 2},
            {"gender": "male", "age": "16", "language": "isiXhosa", "count": 3},
            {"gender": "male", "age": "16", "language": "isiZulu", "count": 4},
            {"gender": "male", "age": "17", "language": "isiXhosa", "count": 5},
            {"gender": "male", "age": "17", "language": "isiZulu", "count": 6},
            {"gender": "female", "age": "15", "language": "isiXhosa", "count": 7},
            {"gender": "female", "age": "15", "language": "isiZulu", "count": 8},
            {"gender": "female", "age": "16", "language": "isiXhosa", "count": 9},
            {"gender": "female", "age": "16", "language": "isiZulu", "count": 10},
            {"gender": "female", "age": "17", "language": "isiXhosa", "count": 11},
            {"gender": "female", "age": "17", "language": "isiZulu", "count": 12},
        ]

    def test_three_geographies(self, indicator, datasetdata2, geographies):
        indicator_data_items = indicator_data_extraction(indicator)
        assert IndicatorData.objects.count() == 3
        assert len(indicator_data_items) == 3

        new_geographies = geographies[1:]

        for g in new_geographies:
            idata = IndicatorData.objects.get(geography=g)
            assert idata.data[0]["geography"] == g.pk

    def test_universe(self, datasetdata, indicator, geographies):
        geography = geographies[0]
        universe = {"data__gender": "female", "data__age__lt": "17"}

        indicator_data_extraction(indicator, universe)
        

        indicator_data = IndicatorData.objects.get(geography=geography)

        assert indicator_data.data == [
            {"gender": "female", "age": "15", "language": "isiXhosa", "count": 7},
            {"gender": "female", "age": "15", "language": "isiZulu", "count": 8},
            {"gender": "female", "age": "16", "language": "isiXhosa", "count": 9},
            {"gender": "female", "age": "16", "language": "isiZulu", "count": 10},
        ]
            


    