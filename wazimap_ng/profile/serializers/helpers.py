from typing import Callable, List, Union

from wazimap_ng.datasets.models import Geography
from wazimap_ng.datasets.models.indicatordata import IndicatorData
from wazimap_ng.profile.models import ProfileHighlight, ProfileKeyMetrics

MetricType = Union[ProfileKeyMetrics, ProfileHighlight]


def get_subindicator(metric: MetricType) -> str:
    subindicators = metric.indicator.subindicators
    idx = metric.subindicator if metric.subindicator is not None else 0
    return subindicators[idx]


def get_sum(data: List[dict], group: str = None, subindicator: str = None) -> float:
    if (group is not None and subindicator is not None):
        return sum([float(row["count"]) for row in data if group in row and row[group] == subindicator])
    return sum(float(row["count"]) for row in data)


class MetricCalculator:
    @staticmethod
    def absolute_value(data: List[dict], metric: MetricType, geography: Geography) -> float:
        group = metric.indicator.groups[0]

        subindicator = get_subindicator(metric)
        filtered_data = [row["count"] for row in data if group in row and row[group] == subindicator]

        return get_sum(data, group, subindicator)

    @staticmethod
    def subindicator(data: List[dict], metric: MetricType, geography: Geography) -> Union[float, None]:
        group = metric.indicator.groups[0]

        subindicator = get_subindicator(metric)
        numerator = get_sum(data, group, subindicator)
        denominator = get_sum(data)

        if denominator > 0 and numerator is not None:
            return numerator / denominator

    @staticmethod
    def sibling(data: List[IndicatorData], metric: MetricType, geography: Geography) -> Union[float, None]:
        group = metric.indicator.groups[0]
        subindicator = get_subindicator(metric)

        numerator = None
        denominator = 0
        total = 0
        geography_total = 0

        for datum in data:
            total += get_sum(datum.data)
            if datum.geography == geography:
                geography_total = get_sum(datum.data)

        denominator, numerator = total, geography_total

        if denominator > 0 and numerator is not None:
            return numerator / denominator

    @staticmethod
    def get_algorithm(algorithm: str, default: str = "absolute_value") -> Callable:
        return {
            "absolute_value": MetricCalculator.absolute_value,
            "sibling": MetricCalculator.sibling,
            "subindicators": MetricCalculator.subindicator
        }.get(algorithm, default)
