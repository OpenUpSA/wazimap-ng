# Generated by Django 2.2.10 on 2020-04-07 11:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0009_auto_20200406_1849'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profilekeymetrics',
            options={'ordering': ['id'], 'verbose_name_plural': 'Profile key metrics'},
        ),
    ]
