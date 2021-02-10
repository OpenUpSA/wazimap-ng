import pytest


from wazimap_ng.datasets.tasks.indicator_data_extraction import indicator_data_extraction

@pytest.mark.django_db
class TestIndicatorDataExtract:

    def test_basic(self, indicator, datasetdatas, groups):

        indicator_data_extraction(indicator)
        assert indicator.indicatordata_set.count() == 1
        indicator_data = indicator.indicatordata_set.first()

        assert indicator_data.data == {
            "groups": {
                "gender": {
                    "male": [
                        {"count": 11.0, "subindicator": "15-19"},
                        {"count": 21.0, "subindicator": "20-24"},
                        {"count": 31.0, "subindicator": "25-29"}
                    ],
                    "female": [
                        {"count": 10.0, "subindicator": "15-19"},
                        {"count": 20.0, "subindicator": "20-24"},
                        {"count": 30.0, "subindicator": "25-29"}
                    ]
                }
            },
            "subindicators": [
                {"count": 21.0, "subindicator": "15-19"},
                {"count": 41.0, "subindicator": "20-24"},
                {"count": 61.0, "subindicator": "25-29"},
            ]
        }

    def test_non_aggregate_non_primary_group(self, indicator, datasetdatas, groups):
        g = groups[-1]
        assert g.name == "gender"
        g.can_aggregate = False
        g.save()


        indicator_data_extraction(indicator)
        indicator_data = indicator.indicatordata_set.first()

        assert indicator_data.data == {
            "groups": {
                "gender": {
                    "male": [
                        {"count": 11.0, "subindicator": "15-19"},
                        {"count": 21.0, "subindicator": "20-24"},
                        {"count": 31.0, "subindicator": "25-29"}
                    ],
                    "female": [
                        {"count": 10.0, "subindicator": "15-19"},
                        {"count": 20.0, "subindicator": "20-24"},
                        {"count": 30.0, "subindicator": "25-29"}
                    ]
                }
            },
            "subindicators": [
                {
                    "group": "15-19",
                    "values": [
                        {"count": 10.0, "subindicator": "female"},
                        {"count": 11.0, "subindicator": "male"},
                    ]
                },
                {
                    "group": "20-24",
                    "values": [
                        {"count": 20.0, "subindicator": "female"},
                        {"count": 21.0, "subindicator": "male"},
                    ]
                },
                {
                    "group": "25-29",
                    "values": [
                        {"count": 30.0, "subindicator": "female"},
                        {"count": 31.0, "subindicator": "male"},
                    ]
                }
            ]
        }
