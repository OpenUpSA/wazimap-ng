from itertools import groupby
from typing import Dict

from django.db.models import F

from wazimap_ng.datasets.models import Group, IndicatorData
from wazimap_ng.profile.models import Profile
from wazimap_ng.utils import qsdict


def get_indicator_data(profile, indicators, geographies, version):

    data = (IndicatorData.objects
            .filter(
                indicator__in=indicators,
                indicator__profileindicator__profile=profile,
                geography__in=geographies,
                indicator__dataset__version=version,
            )
            .values(
                profile_indicator_id=F("indicator__profileindicator__id"),
                jsdata=F("data"),
                description=F("indicator__profileindicator__description"),
                indicator_name=F("indicator__name"),
                indicator_group=F("indicator__groups"),
                profile_indicator_label=F("indicator__profileindicator__label"),
                subcategory=F("indicator__profileindicator__subcategory__name"),
                subcategory_id=F("indicator__profileindicator__subcategory_id"),
                category=F("indicator__profileindicator__subcategory__category__name"),
                choropleth_method=F("indicator__profileindicator__choropleth_method__name"),
                dataset=F("indicator__dataset"),
                version_name=F("indicator__dataset__version__name"),
                metadata_source=F("indicator__dataset__metadata__source"),
                metadata_description=F("indicator__dataset__metadata__description"),
                metadata_url=F("indicator__dataset__metadata__url"),
                dataset_content_type=F("indicator__dataset__content_type"),
                licence_url=F("indicator__dataset__metadata__licence__url"),
                licence_name=F("indicator__dataset__metadata__licence__name"),
                indicator_chart_configuration=F("indicator__profileindicator__chart_configuration"),
                geography_code=F("geography__code"),
                primary_group=F("indicator__groups"),
                last_updated_at=F("indicator__profileindicator__updated"),
                content_type=F("indicator__profileindicator__content_type"),
                chart_type=F("indicator__profileindicator__chart_type"),
                choropleth_range=F("indicator__profileindicator__choropleth_range"),
                enable_linear_scrubber=F("indicator__profileindicator__enable_linear_scrubber")
            )
            .order_by("indicator__profileindicator__order")
            )

    return data

def get_profile_data(profile, geographies, version):
    return get_indicator_data(profile, profile.indicators.all(), geographies, version)

def get_dataset_groups(profile: Profile) -> Dict:
    dataset_groups = (
        Group.objects
        .filter(dataset__indicator__profileindicator__profile=profile)
        .values(
            "subindicators",
            "dataset",
            "name",
            "can_aggregate",
            "can_filter"
        ).order_by("dataset_id", "name").distinct("dataset_id", "name")
    )

    grouped_datasetdata = groupby(dataset_groups, lambda g: g["dataset"])
    grouped_datasetdata = [(grouper, list(groups)) for grouper, groups in grouped_datasetdata]

    dataset_groups_dict = dict(list(grouped_datasetdata))

    return dataset_groups_dict

def metadata_serializer(obj, dataset_groups_dict):
    return qsdict(obj,
         "category",
         lambda x: "subcategories",
         "subcategory",
         lambda x: "indicators",
         "profile_indicator_label",
         lambda x: {
             "id": x["profile_indicator_id"],
             "description": x["description"],
             "choropleth_method": x["choropleth_method"],
             "last_updated_at": x["last_updated_at"],
             "metadata": {
                 "source": x["metadata_source"],
                 "description": x["metadata_description"],
                 "url": x["metadata_url"],
                 "licence": {
                     "name": x["licence_name"],
                     "url": x["licence_url"]
                 },
                 "primary_group": x["primary_group"][0],
                 "groups": dataset_groups_dict[x["dataset"]],
             },
             "content_type": x["content_type"],
             "dataset_content_type": x["dataset_content_type"],
             "version": x["version_name"],
             "chart_configuration": x["indicator_chart_configuration"],
             "chart_type": x["chart_type"],
             "choropleth_range":x["choropleth_range"],
             "enable_linear_scrubber": x["enable_linear_scrubber"]
         },
     )
