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

    def test_non_aggregate_non_primary_group(self, dataset, datasetdatas, groups):
        return True
        g = groups[-1]
        g.can_aggregate = False
        g.save()


        indicator = IndicatorFactory()
        indicator.dataset = dataset

        indicator_data_extraction(indicator)
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
            'subindicators': [
                {
                    "group": "15-19",
                    "values": [
                        {'count': 10.0, 'gender': 'male'},
                        {'count': 20.0, 'gender': 'female'}
                    ]
                },
                {
                    "group": "20-24",
                    "values": [
                        {'count': 11.0, 'gender': 'male'},
                        {'count': 21.0, 'gender': 'female'}
                    ]
                },
                {
                    "group": "25-29",
                    "values": [
                        {'count': 12.0, 'gender': 'male'},
                        {'count': 22.0, 'gender': 'female'}
                    ]
                }
            ]
        }
