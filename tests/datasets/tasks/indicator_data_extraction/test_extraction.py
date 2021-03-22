import pytest

from tests.datasets.factories import (
    DatasetDataFactory,
    DatasetFactory,
    DatasetFileFactory,
    GeographyFactory,
    GeographyHierarchyFactory,
    IndicatorFactory
)
from wazimap_ng.datasets.models import Geography, IndicatorData
from wazimap_ng.datasets.tasks.indicator_data_extraction import (
    indicator_data_extraction
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
@pytest.mark.usefixtures("datasetdata")
class TestIndicatorDataExtraction:
    def test_basic_extraction(self, indicator, geography, indicatordata_json):

        indicator_data_items = indicator_data_extraction(indicator)

        indicator_data = IndicatorData.objects.get(geography=geography)

        assert indicator_data.data == indicatordata_json

    def test_ensure_no_additional_indicator_data_items_created(self, indicator, geography):
        def no_data(x): return len(x.data) == 0

        assert IndicatorData.objects.count() == 0

        indicator_data_items = indicator_data_extraction(indicator)
        assert len(indicator_data_items) == 1
        assert IndicatorData.objects.count() == 1

        assert all(no_data(idata) for idata in IndicatorData.objects.exclude(geography=geography))

    def test_old_data_deleted(self, indicator):
        def no_data(x): return len(x.data) == 0

        assert IndicatorData.objects.count() == 0

        indicator_data_items = indicator_data_extraction(indicator)
        assert len(indicator_data_items) == 1
        assert IndicatorData.objects.count() == 1

        indicator_data_items = indicator_data_extraction(indicator)
        assert len(indicator_data_items) == 1
        assert IndicatorData.objects.count() == 1

    @pytest.mark.usefixtures("datasetdata2")
    def test_three_geographies(self, indicator, geographies):
        indicator_data_items = indicator_data_extraction(indicator)
        assert IndicatorData.objects.count() == 3
        assert len(indicator_data_items) == 3

        new_geographies = geographies[1:]

        for g in new_geographies:
            idata = IndicatorData.objects.get(geography=g)
            assert idata.data[0]["geography"] == g.pk

    @pytest.mark.usefixtures("datasetdata2")
    def test_universe(self, indicator, geographies):
        geography = geographies[0]
        universe = {"data__gender": "female", "data__age__lt": "17"}

        indicator_data_extraction(indicator, universe=universe)
        indicator_data = IndicatorData.objects.get(geography=geography)

        assert indicator_data.data == [
            {"gender": "female", "age": "15", "language": "isiXhosa", "count": 7},
            {"gender": "female", "age": "15", "language": "isiZulu", "count": 8},
            {"gender": "female", "age": "16", "language": "isiXhosa", "count": 9},
            {"gender": "female", "age": "16", "language": "isiZulu", "count": 10},
        ]
