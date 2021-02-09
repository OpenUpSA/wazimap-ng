import pytest


from wazimap_ng.datasets.tasks.indicator_data_extraction import indicator_data_extraction

@pytest.mark.django_db
class TestIndicatorDataExtract:

    def test_basic(self, indicator, datasetdatas, groups):

        indicator_data_extraction(indicator)
        assert indicator.indicatordata_set.count() == 1
        indicator_data = indicator.indicatordata_set.first()

        assert indicator_data.data == {
            'groups': {
                'gender': {
                    'male': [
                        {'count': 11.0, 'age group': '15-19'},
                        {'count': 21.0, 'age group': '20-24'},
                        {'count': 31.0, 'age group': '25-29'}
                    ],
                    'female': [
                        {'count': 10.0, 'age group': '15-19'},
                        {'count': 20.0, 'age group': '20-24'},
                        {'count': 30.0, 'age group': '25-29'}
                    ]
                }
            },
            'subindicators': {'15-19': 21.0, '20-24': 41.0, '25-29': 61.0}
        }

    
