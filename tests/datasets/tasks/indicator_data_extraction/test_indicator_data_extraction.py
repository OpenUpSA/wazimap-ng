import pytest


from wazimap_ng.datasets.tasks.indicator_data_extraction import indicator_data_extraction

@pytest.mark.django_db
class TestIndicatorDataExtract:

    def test_basic(self, indicator, indicator_data_json):
        indicator_data_extraction(indicator)
        assert indicator.indicatordata_set.count() == 1
        indicator_data = indicator.indicatordata_set.first()

        assert indicator_data.data == indicator_data_json

    def test_non_aggregate_non_primary_group(self, indicator, indicator_data_non_agg_json):
        groups = indicator.dataset.group_set.all()
        groups.filter(name="gender").update(can_aggregate=False)
        


        indicator_data_extraction(indicator)
        indicator_data = indicator.indicatordata_set.first()

        assert indicator_data.data == indicator_data_non_agg_json
