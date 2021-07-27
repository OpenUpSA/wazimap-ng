# Generated by Django 2.2.21 on 2021-07-22 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0047_profileindicator_configuration'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileindicator',
            name='content_type',
            field=models.CharField(choices=[('indicator', 'indicator'), ('html', 'html')], default='indicator', max_length=32),
        ),
    ]
