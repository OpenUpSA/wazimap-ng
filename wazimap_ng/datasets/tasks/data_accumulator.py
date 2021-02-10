from collections import defaultdict

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

    def add_subindicator(self, data_blob):
        subindicators = {}
        data_blob = list(data_blob)
        if len(data_blob) == 0:
            return

        datum_copy = dict(data_blob[0])
        count = datum_copy.pop("count")
        values = list(datum_copy.values())
        if len(values) == 0:
            raise Exception("Missing subindicator in datablob")
        elif len(values) == 1:
            self.data["subindicators"] = self._subindicator_no_groups(data_blob)
        else:
            for datum in data_blob:
                count = datum.pop("count")
                subindicator = datum.pop(self.primary_group)
                values = list(datum.values())
                group2_subindicator = values[0]

                group_dict = subindicators.setdefault(subindicator, {})
                group_dict[group2_subindicator] = count
            subindicators_arr = []
            for group_subindicator, values in subindicators.items():
                subindicators_arr.append({
                    "group": group_subindicator,
                    "values": values
                })

            self.data["subindicators"] = subindicators_arr


    @property
    def subindicators(self):
        return self.data["subindicators"]