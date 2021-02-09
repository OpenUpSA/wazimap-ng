import pytest 
from wazimap_ng.datasets.tasks.indicator_data_extraction import extract_counts

@pytest.mark.django_db
def test_exact_counts(indicator, datasetdatas, geography): 

    qs = indicator.dataset.datasetdata_set.all()
    counts = extract_counts(indicator, qs)

    assert counts == [
        {
            "geography_id": geography.id,
            "data": [
                {
                    "age group": "15-19",
                    "count": 21.0
                },
                {
                    "age group": "20-24",
                    "count": 41.0
                },
                {
                    "age group": "25-29",
                    "count": 61.0
                }
            ]
        }
    ]

    qs_subindicator = qs.filter(**{f"data__gender":  "male"})
    counts = extract_counts(indicator, qs_subindicator)

    assert counts == [
        {
            "geography_id": geography.id,
            "data": [
                {
                    "age group": "15-19",
                    "count": 11.0
                },
                {
                    "age group": "20-24",
                    "count": 21.0
                },
                {
                    "age group": "25-29",
                    "count": 31.0
                }
            ]
        }
    ]


@pytest.mark.django_db
def test_exact_counts_with_non_agg_group(indicator, datasetdatas, groups, geography): 
    groups = indicator.dataset.group_set.all()
    group = groups.last()

    assert group.name == "gender"

    group.can_aggregate = False
    group.save()

    qs = indicator.dataset.datasetdata_set.all()
    counts = extract_counts(indicator, qs)
    counts[0]["data"] = sorted(counts[0]["data"], key=lambda x: x["gender"] + x["age group"])

    assert counts == [
        {
            "geography_id": geography.id,
            "data": [
                {
                    "gender": "female",
                    "age group": "15-19",
                    "count": 10.0
                },
                {
                    "gender": "female",
                    "age group": "20-24",
                    "count": 20.0
                },
                {
                    "gender": "female",
                    "age group": "25-29",
                    "count": 30.0
                },
                {
                    "gender": "male",
                    "age group": "15-19",
                    "count": 11.0
                },
                {
                    "gender": "male",
                    "age group": "20-24",
                    "count": 21.0
                },
                {
                    "gender": "male",
                    "age group": "25-29",
                    "count": 31.0
                }
            ]
        }
    ]
