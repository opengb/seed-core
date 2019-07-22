# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2019, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
from __future__ import unicode_literals

import logging

from django.db import models

from seed.models.property_measures import PropertyMeasure
from seed.models.properties import PropertyState

_log = logging.getLogger(__name__)

# Oops! we override a builtin in some of the models
property_decorator = property


class Scenario(models.Model):
    """
    A scenario is an analysis (simple or detailed) on a property state that could result in
    a small or significant change in the building description. A scenario will typically include
    a set of analysis results and can be linked to other scenarios as the reference case.
    """

    TEMPORAL_STATUS_PRE_RETROFIT = 1
    TEMPORAL_STATUS_POST_RETROFIT = 2
    TEMPORAL_STATUS_BASELINE = 3
    TEMPORAL_STATUS_CURRENT = 4
    TEMPORAL_STATUS_TARGET = 5
    TEMPORAL_STATUS_DESIGN_TARGET = 6

    TEMPORAL_STATUS_TYPES = (
        (TEMPORAL_STATUS_PRE_RETROFIT, 'Pre retrofit'),
        (TEMPORAL_STATUS_POST_RETROFIT, 'Post retrofit'),
        (TEMPORAL_STATUS_BASELINE, 'Baseline'),
        (TEMPORAL_STATUS_CURRENT, 'Current'),
        (TEMPORAL_STATUS_TARGET, 'Target'),
        (TEMPORAL_STATUS_DESIGN_TARGET, 'Design Target'),
    )

    name = models.CharField(max_length=255)
    temporal_status = models.IntegerField(choices=TEMPORAL_STATUS_TYPES,
                                          default=TEMPORAL_STATUS_CURRENT)
    description = models.TextField(null=True)

    property_state = models.ForeignKey('PropertyState', related_name='scenarios')

    # a scenario can point to a reference case scenario
    reference_case = models.ForeignKey('Scenario', null=True)

    # package of measures fields
    annual_site_energy_savings = models.FloatField(null=True)
    annual_source_energy_savings = models.FloatField(null=True)
    annual_electricity_savings = models.FloatField(null=True)
    annual_natural_gas_savings = models.FloatField(null=True)
    annual_cost_savings = models.FloatField(null=True)
    summer_peak_load_reduction = models.FloatField(null=True)
    winter_peak_load_reduction = models.FloatField(null=True)
    annual_site_energy = models.FloatField(null=True)
    annual_natural_gas_energy = models.FloatField(null=True)
    annual_electricity_energy = models.FloatField(null=True)
    annual_peak_demand = models.FloatField(null=True)
    hdd = models.FloatField(null=True)
    hdd_base_temperature = models.FloatField(null=True)
    cdd = models.FloatField(null=True)
    cdd_base_temperature = models.FloatField(null=True)

    analysis_start_time = models.DateTimeField(null=True)
    analysis_end_time = models.DateTimeField(null=True)
    # use the analysis states that are defined in the PropertyState model
    analysis_state = models.IntegerField(choices=PropertyState.ANALYSIS_STATE_TYPES,
                                         default=PropertyState.ANALYSIS_STATE_NOT_STARTED)
    analysis_state_message = models.TextField(null=True)

    measures = models.ManyToManyField(PropertyMeasure)

    # TODO: add in meters -- meters are linked from Class Meter
