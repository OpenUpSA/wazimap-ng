# Generated by Django 2.2.24 on 2021-11-11 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0046_historicalcategory_historicalcoordinatefile_historicalprofilecategory_historicaltheme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalcategory',
            name='history_change_reason',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='historicalcoordinatefile',
            name='history_change_reason',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='historicalprofilecategory',
            name='history_change_reason',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='historicaltheme',
            name='history_change_reason',
            field=models.TextField(null=True),
        ),
    ]
