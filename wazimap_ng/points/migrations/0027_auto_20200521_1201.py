# Generated by Django 2.2.10 on 2020-05-21 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0026_auto_20200521_0800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilecategory',
            name='permission_type',
            field=models.CharField(choices=[('private', 'Private'), ('public', 'Public')], default='private', max_length=32),
        ),
    ]
