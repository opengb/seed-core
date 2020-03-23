# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2019, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author nicholas.long@nrel.gov
"""

import logging
import os
import re
from io import StringIO

from django.db.models import FieldDoesNotExist
from quantityfield import ureg
from lxml import etree
import xmlschema

from config.settings.common import BASE_DIR
from seed.models.meters import Meter
from seed.building_sync.mappings import (
    BASE_MAPPING_V2_PR1,
    BASE_MAPPING_V2_0,
    BUILDINGSYNC_URI,
    NAMESPACES,
    merge_mappings,
    apply_mapping,
    update_tree
)

_log = logging.getLogger(__name__)

# Setup lxml parser
parser = etree.XMLParser(remove_blank_text=True)
etree.set_default_parser(parser)
etree.register_namespace('auc', BUILDINGSYNC_URI)


class BuildingSync(object):
    BUILDINGSYNC_V2_PR1 = '2.0-pr1'
    BUILDINGSYNC_V2_0 = '2.0'
    VERSION_MAPPINGS_DICT = {
        BUILDINGSYNC_V2_PR1: BASE_MAPPING_V2_PR1,
        BUILDINGSYNC_V2_0: BASE_MAPPING_V2_0,
    }

    def __init__(self):
        self.filename = None
        self.data = None
        self.raw_data = {}
        self.element_tree = None
        self.version = None

    def import_file(self, filename):
        self.filename = filename

        if not os.path.isfile(filename):
            raise Exception("File not found: {}".format(filename))

        # save element tree
        with open(filename) as f:
            self.element_tree = etree.parse(f)

        # TODO: once xml translator has been implemented and used to convert
        # files from 2.0-pr1 to 2.0, REMOVE the default argument so it fails
        # if no proper version is found
        self.version = self._parse_version(default=self.BUILDINGSYNC_V2_PR1)

        # if the namespace map is missing the auc prefix, fix the tree to include it
        if self.element_tree.getroot().nsmap.get('auc') is None:
            self.fix_namespaces()

        return True

    def fix_namespaces(self):
        """This method should be called when auc prefix is missing from the namespace map.
        It will clone the tree, ensuring all nodes have the proper namespace prefixes
        """
        original_tree = self.element_tree

        etree.register_namespace('auc', BUILDINGSYNC_URI)
        self.init_tree(version=self.version)
        new_root = self.element_tree.getroot()
        original_root = original_tree.getroot()

        def clone_subtree(original, new):
            for child in original.iterchildren():
                new_child = etree.Element(child.tag)
                # update text
                new_child.text = child.text
                # update attributes
                for attr, val in child.items():
                    new_child.set(attr, val)
                new.append(new_child)
                clone_subtree(child, new_child)

        clone_subtree(original_root, new_root)

    def init_tree(self, version=BUILDINGSYNC_V2_0):
        """Initializes the tree with a BuildingSync root node

        :param version: string, should be one of the valid BuildingSync versions
        """
        if version not in self.VERSION_MAPPINGS_DICT:
            raise Exception(f'Invalid version "{version}"')

        xml_string = '''<?xml version="1.0"?>
        <auc:BuildingSync xmlns:auc="http://buildingsync.net/schemas/bedes-auc/2019" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://buildingsync.net/schemas/bedes-auc/2019 https://raw.githubusercontent.com/BuildingSync/schema/v{}/BuildingSync.xsd">
        </auc:BuildingSync>'''.format(version)
        self.element_tree = etree.parse(StringIO(xml_string))
        self.version = version

    def export(self, property_state, custom_mapping=None):
        """Export BuildingSync file from an existing BuildingSync file (from import), property_state and
        a custom mapping.

        :param property_state: object, PropertyState to merge into BuildingSync
        :param custom_mapping: dict, user-defined mapping (used with higher priority over the default mapping)
        :return: string, as XML
        """
        if not property_state:
            return etree.tostring(self.element_tree, pretty_print=True).decode()

        if not self.element_tree:
            self.init_tree(version=BuildingSync.BUILDINGSYNC_V2_0)

        merged_mappings = merge_mappings(self.VERSION_MAPPINGS_DICT[self.version], custom_mapping)
        schema = self.get_schema(self.version)

        # iterate through the 'property' field mappings doing the following
        # - if the property_state has the field, update the xml with that value
        # - else, ignore it
        base_path = merged_mappings['property']['xpath']
        field_mappings = merged_mappings['property']['properties']
        for field, mapping in field_mappings.items():
            if mapping['xpath'].startswith('./'):
                mapping_path = mapping['xpath'][2:]
            else:
                mapping_path = mapping['xpath']
            absolute_xpath = os.path.join(base_path, mapping_path)

            value = None
            try:
                property_state._meta.get_field(field)
                value = getattr(property_state, field)
            except FieldDoesNotExist:
                _log.debug("Field {} is not a db field, trying read from extra data".format(field))
                value = property_state.extra_data.get(field, None)

            if value is None:
                continue
            if isinstance(value, ureg.Quantity):
                value = value.magnitude

            update_tree(schema, self.element_tree, absolute_xpath,
                        mapping['value'], str(value), NAMESPACES)

        return etree.tostring(self.element_tree, pretty_print=True).decode()

    @classmethod
    def get_schema(cls, version):
        schema_dir = os.path.join(BASE_DIR, 'seed', 'building_sync', 'schemas')
        if version == cls.BUILDINGSYNC_V2_PR1:
            schema_path = os.path.join(schema_dir, 'BuildingSync_v2_pr1.xsd')
        elif version == cls.BUILDINGSYNC_V2_0:
            schema_path = os.path.join(schema_dir, 'BuildingSync_v2_0.xsd')
        else:
            raise Exception(f'Unknown file version "{version}"')

        return xmlschema.XMLSchema(schema_path)

    def restructure_mapped_result(self, result, messages):
        """Transforms the dict from applying a mapping into a more standardized structure
        for SEED to store into a model

        :param result: dict, the mapped values
        :param messages: dict, dictionary for recording warnings and errors
        :return: dict, restructured dictionary
        """
        measures = []
        for measure in result['measures']:
            if measure['category'] == '':
                messages['warnings'].append(f'Skipping measure {measure["name"]} due to missing category')
                continue

            measures.append(measure)

        scenarios = []
        for scenario in result['scenarios']:
            # process the scenario meters (aka resource uses)
            meters = {}
            for resource_use in scenario['resource_uses']:
                meter = {}
                meter['source'] = Meter.BUILDINGSYNC
                meter['source_id'] = resource_use['source_id']
                meter['type'] = resource_use['type']
                meter['units'] = resource_use['units']
                meter['is_virtual'] = scenario['is_virtual']
                meter['readings'] = []

                meters[meter['source_id']] = meter

            # process the scenario meter readings
            for series_data in scenario['time_series']:
                reading = {}
                reading['start_time'] = series_data['start_time']
                reading['end_time'] = series_data['end_time']
                reading['reading'] = series_data['reading']
                reading['source_id'] = series_data['source_id']
                reading['source_unit'] = meters[reading['source_id']].get('units')

                # add reading to the meter
                meters[reading['source_id']]['readings'].append(reading)

            # create scenario
            seed_scenario = {}
            seed_scenario['id'] = scenario['id']
            seed_scenario['name'] = scenario['name']
            seed_scenario['reference_case'] = scenario['reference_case']
            seed_scenario['annual_site_energy_savings'] = scenario['annual_site_energy_savings']
            seed_scenario['annual_source_energy_savings'] = scenario['annual_source_energy_savings']
            seed_scenario['annual_cost_savings'] = scenario['annual_cost_savings']
            seed_scenario['annual_electricity_savings'] = scenario['annual_electricity_savings']
            seed_scenario['annual_natural_gas_savings'] = scenario['annual_natural_gas_savings']
            seed_scenario['annual_site_energy'] = scenario['annual_site_energy']
            seed_scenario['annual_site_energy_use_intensity'] = scenario['annual_site_energy_use_intensity']
            seed_scenario['annual_source_energy'] = scenario['annual_source_energy']
            seed_scenario['annual_source_energy_use_intensity'] = scenario['annual_source_energy_use_intensity']
            seed_scenario['annual_electricity_energy'] = scenario['annual_electricity_energy']
            seed_scenario['annual_peak_demand'] = scenario['annual_peak_demand']
            seed_scenario['annual_natural_gas_energy'] = scenario['annual_natural_gas_energy']
            seed_scenario['measures'] = [id['id'] for id in scenario['measure_ids']]

            seed_scenario['meters'] = list(meters.values())
            scenarios.append(seed_scenario)

        res = {'measures': measures, 'scenarios': scenarios}
        # property fields are at the root of the object
        for k, v in result['property'].items():
            res[k] = v

        return res

    def _process_struct(self, base_mapping, custom_mapping=None):
        """Internal call for processing the xml data into data for SEED

        :param base_mapping: dict, a base mapping object; see mappings.py
        :param custom_mapping: dict, another mapping object which is given higher priority over base_mapping
        :return: list, [dict, dict], [results, dict of errors and warnings]
        """
        merged_mappings = merge_mappings(base_mapping, custom_mapping)
        messages = {'warnings': [], 'errors': []}
        result = apply_mapping(self.element_tree, merged_mappings, messages, NAMESPACES)

        # turn result into SEED structure
        seed_result = self.restructure_mapped_result(result, messages)

        return seed_result, messages

    def process(self, custom_mapping=None):
        """Process the BuildingSync file based on the process structure.

        :param process_struct: dict, user-defined structure on how to extract data from file and save into dict
        :return: list, [dict, dict], [results, dict of errors and warnings]
        """
        # API call to BuildingSync Selection Tool on other server for appropriate use case
        # prcess_struct = new_use_case (from Building Selection Tool)
        base_mapping = self.VERSION_MAPPINGS_DICT.get(self.version)
        if base_mapping is None:
            raise Exception(f'Version of BuildingSync object is not supported: "{self.version}"')

        return self._process_struct(base_mapping, custom_mapping)

    def _parse_version(self, default=None):
        """Attempts to get the schema version from the imported data. Raises an exception if
        none is found or if it's an invalid version

        :return: string, schema version (raises Exception when not found or invalid)
        """
        if self.element_tree is None:
            raise Exception('A file must first be imported with import method')

        bsync_element = self.element_tree.getroot()
        if not bsync_element.tag.endswith('BuildingSync'):
            raise Exception('Expected BuildingSync element as root element in xml')

        schemas = bsync_element.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation', '').split()
        schema_regex = r'^https\:\/\/raw\.githubusercontent\.com\/BuildingSync\/schema\/v((\d+\.\d+)(-pr\d+)?)\/BuildingSync\.xsd$'

        for schema_def in schemas:
            schema_search = re.search(schema_regex, schema_def)
            if schema_search:
                parsed_version = schema_search.group(1)
                if parsed_version in self.VERSION_MAPPINGS_DICT:
                    return parsed_version

                raise Exception(f'Unsupported BuildingSync schema version "{parsed_version}". Supported versions: {list(self.VERSION_MAPPINGS_DICT.keys())}')

        if default is not None:
            _log.warn(f'Unable to parse BuildingSync version. Using provided default of "{default}"')
            return default

        raise Exception(f'Invalid or missing schema specification. Expected a schema reference in root element matching the regex: {schema_regex}')
