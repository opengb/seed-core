# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-18 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0020_auto_20160725_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertyview',
            name='labels',
            field=models.ManyToManyField(to='seed.StatusLabel'),
        ),
        migrations.AddField(
            model_name='taxlotview',
            name='labels',
            field=models.ManyToManyField(to='seed.StatusLabel'),
        ),
    ]
