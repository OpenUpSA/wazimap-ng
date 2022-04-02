import pytest

from tests.datasets.factories import (
    DatasetDataFactory,
    DatasetFileFactory,
    GeographyFactory,
    GeographyHierarchyFactory,
    IndicatorFactory,
    UniverseFactory
)
from wazimap_ng.datasets.models import Geography, IndicatorData
from wazimap_ng.datasets.tasks.indicator_data_extraction import (
    indicator_data_extraction
)


@pytest.fixture
def universe():
    return UniverseFactory(
        filters={"gender": "female", "age__lt": "17"}
    )

@pytest.mark.django_db
@pytest.mark.usefixtures("datasetdata")
class TestIndicatorDataExtraction:
    def test_basic_extraction(self, indicator, geography, indicatordata_json):

        indicator_data_extraction(indicator)

        indicator_data = IndicatorData.objects.get(geography=geography)

        assert indicator_data.data == indicatordata_json

    def test_ensure_no_additional_indicator_data_items_created(self, indicator, geography):
        def no_data(x): return len(x.data) == 0

        assert IndicatorData.objects.count() == 0
        indicator_data_extraction(indicator)
        assert IndicatorData.objects.count() == 1

        assert all(no_data(idata) for idata in IndicatorData.objects.exclude(geography=geography))

    def test_old_data_deleted(self, indicator):
        def no_data(x): return len(x.data) == 0

        assert IndicatorData.objects.count() == 0

        indicator_data_extraction(indicator)
        assert IndicatorData.objects.count() == 1

        indicator_data_extraction(indicator)
        assert IndicatorData.objects.count() == 1

    @pytest.mark.usefixtures("child_datasetdata")
    @pytest.mark.usefixtures("child_geographies")
    def test_three_geographies(self, indicator, geography):
        indicator_data_extraction(indicator)
        num_geographies = 1 + geography.get_children().count()
        assert IndicatorData.objects.count() == num_geographies

        new_geographies = geography.get_children()

        for g in geography.get_children():
            idata = IndicatorData.objects.get(geography=g)
            assert idata.data[0]["geography"] == g.pk

    def test_universe(self, indicator, geography, universe):
        # Add universe to indicator
        indicator.universe = universe
        indicator.save()

        indicator_data_extraction(indicator, universe=universe)
        indicator_data = IndicatorData.objects.get(geography=geography)

        assert indicator_data.data == [
            {"gender": "female", "age": "15", "language": "isiXhosa", "count": 7},
            {"gender": "female", "age": "15", "language": "isiZulu", "count": 8},
            {"gender": "female", "age": "16", "language": "isiXhosa", "count": 9},
            {"gender": "female", "age": "16", "language": "isiZulu", "count": 10},
        ]
