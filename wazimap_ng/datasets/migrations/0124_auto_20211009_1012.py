# Generated by Django 2.2.24 on 2021-10-09 10:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0122_auto_20211008_0540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geographyhierarchy',
            name='root_geography',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datasets.Geography', unique=True),
        ),
    ]
