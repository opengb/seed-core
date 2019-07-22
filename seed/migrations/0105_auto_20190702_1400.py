# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-02 21:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0104_auto_20190509_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenario',
            name='annual_electricity_energy',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='scenario',
            name='annual_electricity_savings',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='scenario',
            name='annual_natural_gas_energy',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='scenario',
            name='annual_natural_gas_savings',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='scenario',
            name='annual_peak_demand',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='scenario',
            name='annual_site_energy',
            field=models.FloatField(null=True),
        ),
    ]
