# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
import logging

from django.test import TestCase

from seed.landing.models import SEEDUser as User
from seed.lib.merging.merging import get_state_to_state_tuple
from seed.test_helpers.fake import (
    FakePropertyViewFactory,
    FakeTaxLotViewFactory
)
from seed.utils.organizations import create_organization

logger = logging.getLogger(__name__)


class StateFieldsTest(TestCase):
    """Tests that our logic for constructing cleaners works."""

    def setUp(self):
        self.maxDiff = None
        user_details = {
            'username': 'test_user@demo.com',
            'password': 'test_pass',
        }
        self.user = User.objects.create_superuser(
            email='test_user@demo.com', **user_details
        )
        self.org, _, _ = create_organization(self.user)
        self.taxlot_view_factory = FakeTaxLotViewFactory(organization=self.org)
        self.property_view_factory = FakePropertyViewFactory(organization=self.org, user=self.user)

    def test_property_state(self):
        property_view_1 = self.property_view_factory.get_property_view()
        tax_lot_view_1 = self.taxlot_view_factory.get_taxlot_view()

        print property_view_1
        print tax_lot_view_1

        expected = ((u'address_line_1', u'address_line_1'), (u'address_line_2', u'address_line_2'),
                    (u'analysis_end_time', u'analysis_end_time'), (u'analysis_start_time', u'analysis_start_time'),
                    (u'analysis_state', u'analysis_state'), (u'analysis_state_message', u'analysis_state_message'),
                    (u'building_certification', u'building_certification'), (u'building_count', u'building_count'),
                    (u'city', u'city'), (u'conditioned_floor_area', u'conditioned_floor_area'),
                    (u'custom_id_1', u'custom_id_1'), (u'energy_alerts', u'energy_alerts'),
                    (u'energy_score', u'energy_score'), (u'generation_date', u'generation_date'),
                    (u'gross_floor_area', u'gross_floor_area'), (u'home_energy_score_id', u'home_energy_score_id'),
                    (u'jurisdiction_property_id', u'jurisdiction_property_id'),
                    (u'latitude', u'latitude'), (u'longitude', u'longitude'), (u'lot_number', u'lot_number'),
                    (u'normalized_address', u'normalized_address'), (u'occupied_floor_area', u'occupied_floor_area'),
                    (u'owner', u'owner'), (u'owner_address', u'owner_address'),
                    (u'owner_city_state', u'owner_city_state'),
                    (u'owner_email', u'owner_email'), (u'owner_postal_code', u'owner_postal_code'),
                    (u'owner_telephone', u'owner_telephone'), (u'pm_parent_property_id', u'pm_parent_property_id'),
                    (u'pm_property_id', u'pm_property_id'), (u'postal_code', u'postal_code'),
                    (u'property_name', u'property_name'), (u'property_notes', u'property_notes'),
                    (u'property_type', u'property_type'), (u'recent_sale_date', u'recent_sale_date'),
                    (u'release_date', u'release_date'), (u'site_eui', u'site_eui'),
                    (u'site_eui_modeled', u'site_eui_modeled'),
                    (u'site_eui_weather_normalized', u'site_eui_weather_normalized'), (u'source_eui', u'source_eui'),
                    (u'source_eui_modeled', u'source_eui_modeled'),
                    (u'source_eui_weather_normalized', u'source_eui_weather_normalized'),
                    (u'space_alerts', u'space_alerts'), (u'state', u'state'), (u'ubid', u'ubid'),
                    (u'use_description', u'use_description'), (u'year_built', u'year_built'),
                    (u'year_ending', u'year_ending'))

        result = get_state_to_state_tuple(self.org, 'PropertyState')
        self.assertSequenceEqual(expected, result)

    def test_taxlot_state(self):
        expected = (
            (u'address_line_1', u'address_line_1'), (u'address_line_2', u'address_line_2'),
            (u'block_number', u'block_number'), (u'city', u'city'), (u'custom_id_1', u'custom_id_1'),
            (u'district', u'district'), (u'jurisdiction_tax_lot_id', u'jurisdiction_tax_lot_id'),
            (u'normalized_address', u'normalized_address'), (u'number_properties', u'number_properties'),
            (u'postal_code', u'postal_code'), (u'state', u'state'))
        result = get_state_to_state_tuple(self.org, u'TaxLotState')
        self.assertSequenceEqual(expected, result)
