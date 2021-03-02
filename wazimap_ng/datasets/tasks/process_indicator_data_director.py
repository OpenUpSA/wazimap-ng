
import logging

from django.db import transaction

logger = logging.getLogger(__name__)

@transaction.atomic
def process_indicator_data_director(indicator_indicator_json, **kwargs):
    logger.debug(f"process_uploaded director file: {indicator_indicator_json}")


    # filename = indicator_director.document.name
    # if ".json" in filename:
        
    # sorter = Sorter()
    # primary_group = indicator.groups[0] # TODO ensure that we only ever have one primary group. Probably need to change the model

    # models.IndicatorData.objects.filter(indicator=indicator).delete()
    # groups = ["data__" + i for i in indicator.dataset.groups]

    # for group in indicator.dataset.groups:
    #     logger.debug(f"Extracting subindicators for: {group}")
    #     qs = models.DatasetData.objects.filter(dataset=indicator.dataset, data__has_keys=[group])
    #     if group != primary_group:
    #         subindicators = qs.get_unique_subindicators(group)

    #         for subindicator in subindicators:
    #             logger.debug(f"Extracting subindicators for: {group} -> {subindicator}")
    #             qs_subindicator = qs.filter(**{f"data__{group}": subindicator})

    #             counts = extract_counts(indicator, qs_subindicator)
    #             sorter.add_data(group, subindicator, counts)
    #     else:
    #         counts = extract_counts(indicator, qs)
    #         sorter.add_subindicator(counts)


    # datarows = []
    # for geography_id, accumulator in sorter.accumulators.items():
    #     datarows.append(models.IndicatorData(
    #         indicator=indicator, geography_id=geography_id, data=accumulator.data
    #     )
    # )

    # models.IndicatorData.objects.bulk_create(datarows, 1000)

    return { }  