# Generated by Django 2.2.28 on 2022-07-26 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0053_auto_20220719_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalprofileindicator',
            name='enable_linear_scrubber',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profileindicator',
            name='enable_linear_scrubber',
            field=models.BooleanField(default=False),
        ),
    ]
