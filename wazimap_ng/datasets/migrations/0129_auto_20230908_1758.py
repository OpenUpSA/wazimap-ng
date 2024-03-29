# Generated by Django 2.2.28 on 2023-09-08 17:58

import django.core.validators
from django.db import migrations, models
import wazimap_ng.datasets.models.upload


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0128_auto_20220711_0723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasetfile',
            name='document',
            field=models.FileField(help_text='\n            Uploaded document should be less than 1000.0 MiB in size and\n            file extensions should be one of csv, xls, xlsx.\n        ', upload_to=wazimap_ng.datasets.models.upload.get_file_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['csv', 'xls', 'xlsx']), wazimap_ng.datasets.models.upload.file_size]),
        ),
        migrations.AlterField(
            model_name='historicaldatasetfile',
            name='document',
            field=models.TextField(help_text='\n            Uploaded document should be less than 1000.0 MiB in size and\n            file extensions should be one of csv, xls, xlsx.\n        ', max_length=100, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['csv', 'xls', 'xlsx']), wazimap_ng.datasets.models.upload.file_size]),
        ),
    ]
