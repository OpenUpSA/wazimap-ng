import operator
from collections import Counter, OrderedDict

from wazimap_ng.utils import sort_list_using_order


class SubindicatorSorter:
    def __init__(self, group_orders):
        self._group_orders = group_orders

    def sort_subindicators(self, subindicators, group):
        sorted_dict = subindicators

        sort_order = self._group_orders.get(group, None)

        if sort_order is not None:
            unique_sort_order = list(Counter(sort_order).keys())
            sorted_tuples = sort_list_using_order(subindicators.items(), unique_sort_order, operator.itemgetter(0))
            sorted_dict = OrderedDict(sorted_tuples)

        return sorted_dict

    def sort_groups(self, groups, primary_group):
        new_dict = OrderedDict()
        for group, group_subindicators in groups.items():
            sorted_group_subindicators = OrderedDict(self.sort_subindicators(group_subindicators, group))

            for group_subindicator, subindicators in sorted_group_subindicators.items():
                sorted_group_subindicators[group_subindicator] = self.sort_subindicators(subindicators, primary_group)

            new_dict[group] = sorted_group_subindicators

        return new_dict
