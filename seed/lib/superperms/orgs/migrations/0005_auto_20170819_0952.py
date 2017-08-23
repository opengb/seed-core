# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-08-19 16:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0004_organization_measurement_system'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='measurement_system',
        ),
        migrations.AddField(
            model_name='organization',
            name='measurement_system_display',
            field=models.IntegerField(choices=[(1, b'United States customary units - kBtu/sq ft'), (2, b'Metric (SI) units - GJ/m2'), (3, b'Metric (SI) units - kWh/m2')], default=1),
        ),
        migrations.AddField(
            model_name='organization',
            name='measurement_system_import',
            field=models.IntegerField(choices=[(1, b'United States customary units - kBtu/sq ft'), (2, b'Metric (SI) units - GJ/m2'), (3, b'Metric (SI) units - kWh/m2')], default=1),
        ),
    ]
