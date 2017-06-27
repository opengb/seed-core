# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-06-22 21:53
from __future__ import unicode_literals

from django.db import migrations
import seed.models.properties


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0070_propertystate_site_eui_ogbs'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertystate',
            name='conditioned_floor_area_ogbs',
            field=seed.models.properties.QuantityField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertystate',
            name='gross_floor_area_ogbs',
            field=seed.models.properties.QuantityField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertystate',
            name='occupied_floor_area_ogbs',
            field=seed.models.properties.QuantityField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertystate',
            name='site_eui_weather_normalized_ogbs',
            field=seed.models.properties.QuantityField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertystate',
            name='source_eui_ogbs',
            field=seed.models.properties.QuantityField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertystate',
            name='source_eui_weather_normalized_ogbs',
            field=seed.models.properties.QuantityField(blank=True, null=True),
        ),
    ]
