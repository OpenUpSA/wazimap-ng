from django import forms
from ... import models

class IndicatorDirectorForm(forms.Form):
    dataset = forms.ModelChoiceField(queryset=models.Dataset.objects.all(), required=True)
    json_data = forms.FileField(required=False)

    def process_json(self, dataset, json_data):
        pass
        # reader = csv.DictReader(StringIO(csv_data.read().decode('utf-8')), delimiter=';')
        # bulk_create_manager = BulkCreateManager(chunk_size=500)
        # existing_scans = Scan.objects.by_campaign(campaign.company, campaign.id)

        # if existing_scans.exists():
        #     logger.info('Deleting existing data found for campaign %s', campaign)
        #     existing_scans.delete()

        # for row in reader:
        #     bulk_create_manager.add(Scan(
        #         campaign=campaign,
        #         scan_date=row.get('scandate'),
        #         timezone=row.get('timezone'),
        #         anonymized_ip=row.get('anonymizedip'),
        #         longitude=row['lng'],
        #         latitude=row['lat']]
        #     ))
        # bulk_create_manager.done()
        # logger.info('Successfully imported scan data for campaign %s', campaign)