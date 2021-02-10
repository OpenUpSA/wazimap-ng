from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class DataAccumulator:
    def __init__(self, geography_id, primary_group=None):
        self.geography_id = geography_id
        self.data = {
            "groups": defaultdict(dict),
            "subindicators": {}
        }

        self.primary_group = primary_group

    def add_data(self, group, subindicator, data_blob):
        self.data["groups"][group][subindicator] = data_blob["data"]

    def _subindicator_no_groups(self, data_blob):
        subindicators = []
        for datum in data_blob:
            count = datum.pop("count")
            values = list(datum.values())
            subindicator = values[0]
            subindicators.append({"subindicator": subindicator, "count": count})

        return subindicators

    def _subindicator_groups(self, data_blob):
        subindicators = {}
        subindicators_arr = []

        for datum in data_blob:
            count = datum.pop("count")
            subindicator = datum.pop(self.primary_group)
            values = list(datum.values())
            if len(values) > 1:
                logger.warning(f"Data cannot be grouped by more than one group. The first group will be selected.")
            group2_subindicator = values[0]

            group_data = subindicators.setdefault(subindicator, [])
            group_data.append({"subindicator": group2_subindicator, "count": count})

        for group_subindicator, values in subindicators.items():
            subindicators_arr.append({
                "group": group_subindicator,
                "values": values
            })

        return subindicators_arr

    def get_groups(self, data_blob):
        data_blob = list(data_blob)
        if len(data_blob) == 0:
            return

        datum_copy = dict(data_blob[0])
        count = datum_copy.pop("count")
        return list(datum_copy.keys())

    def add_subindicator(self, data_blob):
        data_blob = list(data_blob)
        groups = self.get_groups(data_blob)
        if len(groups) == 0:
            raise Exception("Missing subindicator in datablob")
        elif len(groups) == 1:
            self.data["subindicators"] = self._subindicator_no_groups(data_blob)
        else:
            self.data["subindicators"] = self._subindicator_groups(data_blob)


    @property
    def subindicators(self):
        return self.data["subindicators"]