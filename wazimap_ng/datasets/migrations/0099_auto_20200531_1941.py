# Generated by Django 2.2.10 on 2020-05-31 19:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0098_group_dataset'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('name',), 'verbose_name': 'SubindicatorsGroup'},
        ),
        migrations.RemoveField(
            model_name='group',
            name='subindicators',
        ),
    ]
