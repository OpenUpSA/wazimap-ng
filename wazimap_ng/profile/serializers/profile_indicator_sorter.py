from wazimap_ng.datasets.models import Group
from wazimap_ng.utils import qsdict

from .subindicator_sorter import SubindicatorSorter


class ProfileIndicatorSorter:
    def __init__(self, profile):
        self._sorters = self._get_sorters(profile)

    def _get_sorters(self, profile):
        groups = (Group.objects
            .filter(dataset__indicator__profileindicator__profile=profile)
            .order_by("dataset")
            .values("name", "dataset", "subindicators")
        )

        grouped_orders = qsdict(groups, "dataset", "name", "subindicators")
        sorters = {ds: SubindicatorSorter(ds_groups) for ds, ds_groups in grouped_orders.items()}
        return sorters

    def _sort_indicators(self, row, sort_func):
        dataset = row["dataset"]
        sorter = self._sorters[dataset]
        groups = row["indicator_group"]
        primary_group = groups[0]

        return sort_func(sorter, primary_group)


    def sort_groups(self, data):
        for row in data:
            group_data = row["jsdata"]["groups"]
            sort_func = lambda sorter, group: sorter.sort_groups(group_data, group)

            row["jsdata"]["groups"] = self._sort_indicators(row, sort_func)

            yield row

    def sort_subindicators(self, data):
        for row in data:
            subindicators = row["jsdata"]["subindicators"]
            sort_func = lambda sorter, group: sorter.sort_subindicators(subindicators, group)
            row["jsdata"]["subindicators"] = self._sort_indicators(row, sort_func)

            yield row

    def sort(self, data):
        data = self.sort_groups(data)
        data = self.sort_subindicators(data)

        return list(data)
