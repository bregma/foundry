""" Subcommand to list entities """

import glob
import os
import sys
import yaml
from ..config.config import Config

_template_directory: str
_workstation_effects: dict

def add_parser(subparsers):
    """ Adds the CLI arguments parser for this subcommand. """
    parser = subparsers.add_parser('list',
                                   help='list entities (incomplete)')
    parser.set_defaults(func=list_command)


def load_crafting_tags(crafting_tags_path):
    crafting_tags = {}
    search_pattern = os.path.join(crafting_tags_path, '*.yaml')
    for file_path in glob.iglob(search_pattern):
        with open(file_path, 'r') as yaml_file:
            resource = yaml.safe_load(yaml_file)
            for key, value in resource['CraftingTag'].items():
                crafting_tags[value['identifier']] = value['name']
    return crafting_tags


def load_industries(industries_path):
    industries = {}
    search_pattern = os.path.join(industries_path, '*.yaml')
    for file_path in glob.iglob(search_pattern):
        with open(file_path, 'r') as yaml_file:
            resource = yaml.safe_load(yaml_file)
            for key, value in resource['IndustryTemplate'].items():
                industries[value['identifier']] = value['name']
    return industries


def load_sales_categories(sales_categories_path):
    sales_categories = {}
    search_pattern = os.path.join(sales_categories_path, '*.yaml')
    for file_path in glob.iglob(search_pattern):
        with open(file_path, 'r') as yaml_file:
            resource = yaml.safe_load(yaml_file)
            for key, value in resource['SalesItemCategoryTemplate'].items():
                sales_categories[value['identifier']] = value['name']
    return sales_categories


def load_workstation_effects() -> dict:
    workstation_effects = {}
    workstation_effects_path = os.path.join(_template_directory, 'WorkstationEffectTagTemplate')
    search_pattern = os.path.join(workstation_effects_path, '*.yaml')
    for file_path in glob.iglob(search_pattern):
        with open(file_path, 'r') as yaml_file:
            resource = yaml.safe_load(yaml_file)
            for key, value in resource['WorkstationEffectTagTemplate'].items():
                workstation_effects[value['identifier']] = value['displayName']
    return workstation_effects

def find_icon(config, icon_id):
    png_path = config["SOURCE"]["png_path"]
    png_file_name = os.path.join(png_path, f'{icon_id}_512.png')
    print(f'--> looking for icon file "{png_file_name}"')
    return png_file_name if os.path.isfile(png_file_name) else ''


class Buildable:

    def __init__(self, item_id: str):
        buildable_object_path = os.path.join(_template_directory, 'BuildableObjectTemplate')
        buildable_obj_file_path = os.path.join(buildable_object_path, item_id) + ".yaml"
        with open(buildable_obj_file_path, 'r') as bf:
            buildable_yaml = yaml.safe_load(bf)
            buildable = buildable_yaml['BuildableObjectTemplate'][item_id]
            self.object_type          = buildable['type']
            self.object_size          = buildable['size']
            self.requires_foundation  = buildable['hasToBeOnFoundation']
            self.is_modular_building  = bool(buildable["isModularBuilding"])
            self.power_subtype        = buildable['powerSubType']
            self.energy_consumption   = buildable['energyConsumptionKW_str']
            self.lvg_connection       = bool(buildable['hasEnergyGridConnection'])
            self.hvg_connection       = bool(buildable['hasPoleGridConnection'])
            self.hvg_connection_max   = int(buildable['poleGrid_maxConnections'])
            self.hvg_connection_range = int(buildable['poleGrid_connectionRange'])
            self.hvg_transmission     = buildable['transformer_transmissionRate_kjPerS_str']
            self.producer_modifier    = buildable['producer_recipeTimeModifier_str']
            self.ws_affects           = None
            self.ws_excludes          = None

            if bool(buildable['hasWorkstationEffectManager']):
                ws_affects_list = []
                for s in buildable['workstationEffectTags']:
                    ws_affects_list.append(_workstation_effects[s.split('|')[0]])
                self.ws_affects       = ', '.join(ws_affects_list)
                ws_excludes_list = []
                for s in buildable['workstationEffectTags']:
                    ws_excludes_list.append(_workstation_effects[s.split('|')[0]])
                self.ws_excludes = ', '.join(ws_excludes_list)

def load_buildable(config: Config, item_id: str) -> (bool, dict):
    """ Finds and loads the BuildableObjectTemplate for an Item, is one exists. """
    buildable_object_path = os.path.join(_template_directory, 'BuildableObjectTemplate')
    buildable_obj_file_path = os.path.join(buildable_object_path, item_id) + ".yaml"
    if config.verbose:
        print(f'  trying buildable object template "{buildable_obj_file_path}" ..')
    try:
        with open(buildable_obj_file_path, 'r') as bf:
            if config.verbose:
                print(f'  .. found')
            buildable = yaml.safe_load(bf)
            return (True, buildable['BuildableObjectTemplate'][item_id])
    except FileNotFoundError:
        if config.verbose:
            print(f'  .. not found')
        pass
    return (False, None)


def list_command(config):
    """ Entry function for importer module. """
    global _template_directory, _workstation_effects

    _template_directory = config["SOURCE"]["template_path"]
    if config.verbose:
        print(f'looking in "{_template_directory}"')
    if not os.path.isdir(_template_directory):
        raise ValueError(f"Provided template path '{_template_directory}' is not a valid directory.")

    crafting_tags = load_crafting_tags(os.path.join(_template_directory, 'CraftingTag'))
    industries = load_industries(os.path.join(_template_directory, 'IndustryTemplate'))
    sales_categories = load_sales_categories(os.path.join(_template_directory, 'SalesItemCategoryTemplate'))
    _workstation_effects = load_workstation_effects()

    item_path = os.path.join(_template_directory, 'ItemTemplate')
    buildable_object_path = os.path.join(_template_directory, 'BuildableObjectTemplate')
    recipe_path = os.path.join(_template_directory, 'CraftingRecipe')
    research_path = os.path.join(_template_directory, 'ResearchTemplate')

    wiki_file_directory = config["OUTPUT"]["wiki_file_path"]

    search_pattern = os.path.join(item_path, '*.yaml')
    for file_path in glob.iglob(search_pattern):
        with open(file_path, 'r') as yaml_file:
            resource = yaml.safe_load(yaml_file)
            for key, value in resource['ItemTemplate'].items():
                name = value['name']
                item_id = value['identifier']
                flags = value['flags']
                recipe_file_path = os.path.join(recipe_path, item_id) + ".yaml"
                icon_id = value['icon_identifier']
                stack_size = value['stackSize']
                is_modular_building = False

                fuel_value     = value['burnable_fuelValueKJ_str']

                si_category    = value['salesItem_salesItemCategoryIdentifier']
                si_industry    = value['salesItem_industryIdentifier']
                si_price       = value['salesItem_currencyAmount']
                si_base_demand = value['salesItem_salesPlatformBaseDemandPerDay']

                ws_data1       = value['workstationItem_data01']
                ws_data1       = value['workstationItem_data02']

                ws_type_list = []
                for s in value['workstationItem_requiredTags']:
                    ws_type_list.append(_workstation_effects[s.split('|')[0]])
                ws_types       = ', '.join(ws_type_list)

                buildable = None
                try:
                    buildable = Buildable(item_id)
                except FileNotFoundError:
                    pass

                made_in = []
                try:
                    with open(recipe_file_path, 'r') as recipe_file:
                        has_recipe = True
                        recipe = yaml.safe_load(recipe_file)
                        for k, v in recipe['CraftingRecipe'].items():
                            made_in = v['tags']
                except FileNotFoundError:
                    has_recipe = False

                if config.verbose:
                    print(f'--> {name} : item_id="{item_id}" flags="{flags}" {"CRAFTABLE" if has_recipe else ""} {"BUILDABLE" if buildable is not None else ""} {"IS_MODULAR" if is_modular_building else ""}')
                wiki_filename = f'{name.strip().replace(" ", "_")}.wiki'
                print(f'--> file="{wiki_filename}"')
                base_template = 'Item'
                if 'CRITTER' in flags:
                    base_template = 'Critter'
                if 'BUILDABLE_OBJECT' in flags:
                    base_template = 'Buildable'
                print('{{'+base_template)
                print(f'| Name                = {name}')
                if stack_size > 0:
                    print(f'| Stack Size          = {stack_size}')
                if fuel_value != '':
                    print(f'| Fuel Value          = {fuel_value}')
                if 'SALES_ITEM' in flags:
                    print(f'| Sales Category      = {sales_categories[si_category]}')
                    print(f'| Sales Industry      = {industries[si_industry]}')
                    print(f'| Sales Price         = {si_price}')
                    print(f'| Sales Base Demand   = {si_base_demand}')
                if 'WORKSTATION_ITEM' in flags:
                    print(f'| Workstation Types   = {ws_types}')
                if buildable is not None:
                    if buildable.object_type != '':
                        print(f'| Type                = {buildable.object_type}')
                    if len(buildable.object_size) == 3:
                        print(f'| Lenth               = {buildable.object_size["x"]}')
                        print(f'| Width               = {buildable.object_size["z"]}')
                        print(f'| Height              = {buildable.object_size["y"]}')
                    if buildable.requires_foundation:
                        print(f'| Requires Foundation = 1')
                    if buildable.lvg_connection:
                        print(f'| Low Voltage Grid    = 1')
                    if 'CONSUMER' in buildable.power_subtype and buildable.energy_consumption != '' and buildable.energy_consumption != '0':
                        print(f'| Energy Consumption  = {buildable.energy_consumption}')
                    if buildable.hvg_connection:
                        print(f'| High Voltage Grid        = 1')
                        print(f'| High Voltage Subtype     = {buildable.power_subtype}')
                        print(f'| High Voltage Connections = {buildable.hvg_connection_max}')
                        print(f'| High Voltage Range       = {buildable.hvg_connection_range}')
                    if 'TRANSFORMER' in buildable.power_subtype and buildable.hvg_transmission != '' and buildable.hvg_transmission != '0':
                        print(f'| High Voltage Transmission = {buildable.hvg_transmission}')
                    if buildable.object_type == 'Producer':
                        print(f'| Production Multiplier = {buildable.producer_modifier}')
                    if 'BUILDABLE_OBJECT' in flags and buildable.ws_affects:
                        print(f'| Workstation Affects = {buildable.ws_affects}')
                        print(f'| Workstation Excludes = {buildable.ws_excludes}')
                print('}}')
                if has_recipe:
                    print('\n== Crafting ==')
                    for maker in made_in:
                        print(f'* {crafting_tags[maker]}')

                print('')
                if has_recipe:
                    print('[[Category:Craftable Objects]]')
                if buildable is not None:
                    if 'BUILDABLE_OBJECT' in flags:
                        print('[[Category:Buildable Objects]]')
                    if 'BURNABLE' in flags:
                        print('[[Category:Burnables]]')
                    if 'CRITTER' in flags:
                        print('[[Category:Critters]]')
                    if buildable.is_modular_building:
                        print('[[Category:Modular Buildings]]')
                    if 'HANDHELD' in flags:
                        print('[[Category:Handhelds]]')
                    if 'SALES_ITEM' in flags:
                        print('[[Category:Sales Items]]')
                    if 'SEED' in flags:
                        print('[[Category:Seeds]]')
                    if 'WORKSTATION_ITEM' in flags:
                        print('[[Category:Workstation Items]]')
                print()
