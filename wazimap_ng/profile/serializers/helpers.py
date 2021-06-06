def get_subindicator(metric):
    subindicators = metric.indicator.subindicators
    idx = metric.subindicator if metric.subindicator is not None else 0
    return subindicators[idx]

def get_sum(data, group=None, subindicator=None):
    if (group is not None and subindicator is not None):
        return sum([float(row["count"]) for row in data if group in row and row[group] == subindicator])
    return sum(float(row["count"]) for row in data)

class MetricCalculator:
    @staticmethod
    def absolute_value(data, metric, geography):
        group = metric.indicator.groups[0]
        subindicator = get_subindicator(metric)
        
        filtered_data = [row["count"] for row in data if group in row and row[group] == subindicator]
            
        return get_sum(data, group, subindicator)

    @staticmethod
    def subindicator(data, metric, geography):
        group = metric.indicator.groups[0]
        subindicator = get_subindicator(metric)

        numerator = get_sum(data, group, subindicator)
        denominator = get_sum(data)

        if denominator > 0 and numerator is not None:
            return numerator / denominator

    @staticmethod
    def sibling(data, metric, geography):
        group = metric.indicator.groups[0]
        subindicator = get_subindicator(metric)

        geography_total = total = 0
        geography_has_data = False

        for datum in data:
            total += get_sum(datum.data, group=group, subindicator=subindicator)
            if datum.geography == geography:
                geography_total = get_sum(datum.data, group=group, subindicator=subindicator)
                geography_has_data = True

        if not geography_has_data:
            return None

        denominator, numerator = total, geography_total        

        if denominator > 0 and numerator is not None:
            return numerator / denominator

    @staticmethod
    def get_algorithm(algorithm, default="absolute_value"):
        return {
            "absolute_value": MetricCalculator.absolute_value,
            "sibling": MetricCalculator.sibling,
            "subindicators": MetricCalculator.subindicator
        }.get(algorithm, default)
