""" Subcommand to list entities """

import glob
import os
import shutil
import sys
import yaml


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


def load_workstation_effects(workstation_effects_path):
    workstation_effects = {}
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


def list_command(config):
    """ Entry function for importer module. """

    template_directory = config["SOURCE"]["template_path"]
    if config.verbose:
        print(f'looking in "{template_directory}"')

    if not os.path.isdir(template_directory):
        raise ValueError(f"Provided template path '{template_directory}' is not a valid directory.")

    crafting_tags = load_crafting_tags(os.path.join(template_directory, 'CraftingTag'))
    industries = load_industries(os.path.join(template_directory, 'IndustryTemplate'))
    sales_categories = load_sales_categories(os.path.join(template_directory, 'SalesItemCategoryTemplate'))
    workstation_effects = load_workstation_effects(os.path.join(template_directory, 'WorkstationEffectTagTemplate'))

    item_path = os.path.join(template_directory, 'ItemTemplate')
    buildable_object_path = os.path.join(template_directory, 'BuildableObjectTemplate')
    recipe_path = os.path.join(template_directory, 'CraftingRecipe')
    research_path = os.path.join(template_directory, 'ResearchTemplate')

    wiki_file_directory = config["OUTPUT"]["wiki_file_path"]

    search_pattern = os.path.join(item_path, '*.yaml')
    for file_path in glob.iglob(search_pattern):
        with open(file_path, 'r') as yaml_file:
            resource = yaml.safe_load(yaml_file)
            for key, value in resource['ItemTemplate'].items():
                name = value['name']
                identifier = value['identifier']
                flags = value['flags']
                buildable_obj_file_path = os.path.join(buildable_object_path, identifier) + ".yaml"
                recipe_file_path = os.path.join(recipe_path, identifier) + ".yaml"
                icon_id = value['icon_identifier']
#                if icon_id != '':
#                    png_file_name = find_icon(config, icon_id)
#                    wiki_file_name = os.path.join(wiki_file_directory, f'{name.replace(" ", "_")}.png')
#                    shutil.copy2(png_file_name, wiki_file_name)
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
                    ws_type_list.append(workstation_effects[s.split('|')[0]])
                ws_types       = ', '.join(ws_type_list)

                object_type         = ''
                object_size         = []
                requires_foundation = False
                power_subtype       = ''
                energy_consumption  = 0
                lvg_connection      = False
                hvg_connection      = False
                hvg_connection_max  = False
                hvg_transmission    = ''
                ws_affects = ''
                ws_excludes = ''
                producer_modifier = ''
                try:
                    with open(buildable_obj_file_path, 'r') as bf:
                        is_buildable = True
                        buildable = yaml.safe_load(bf)
                        for k, v in buildable['BuildableObjectTemplate'].items():
                            object_type         = v['type']
                            object_size         = v['size']
                            requires_foundation = v['hasToBeOnFoundation']
                            is_modular_building = bool(v["isModularBuilding"])
                            power_subtype       = v['powerSubType']
                            energy_consumption  = v['energyConsumptionKW_str']
                            lvg_connection      = bool(v['hasEnergyGridConnection'])
                            hvg_connection      = bool(v['hasPoleGridConnection'])
                            hvg_connection_max  = int(v['poleGrid_maxConnections'])
                            hvg_connection_range= int(v['poleGrid_connectionRange'])
                            hvg_transmission    = v['transformer_transmissionRate_kjPerS_str']
                            producer_modifier   = v['producer_recipeTimeModifier_str']

                            if bool(v['hasWorkstationEffectManager']):
                                ws_affects_list = []
                                for s in v['workstationEffectTags']:
                                    ws_affects_list.append(workstation_effects[s.split('|')[0]])
                                ws_affects       = ', '.join(ws_affects_list)
                                ws_excludes_list = []
                                for s in v['workstationEffectTags']:
                                    ws_excludes_list.append(workstation_effects[s.split('|')[0]])
                                ws_excludess       = ', '.join(ws_excludes_list)
                except FileNotFoundError:
                    is_buildable = False

                made_in = []
                try:
                    with open(recipe_file_path, 'r') as recipe_file:
                        has_recipe = True
                        recipe = yaml.safe_load(recipe_file)
                        for k, v in recipe['CraftingRecipe'].items():
                            made_in = v['tags']
                except FileNotFoundError:
                    has_recipe = False

#                print(f'--> {name} : icon="{icon_id}" png_file_name="{png_file_name}" flags="{flags}" {"CRAFTABLE" if has_recipe else ""} {"BUILDABLE" if is_buildable else ""} {"IS_MODULAR" if is_modular_building else ""} stack size = {stack_size}')
                wiki_filename = f'{name.strip().replace(" ", "_")}.wiki'
                print(f'--> file="{wiki_filename}"')
                base_template = 'Item'
                if 'CRITTER' in flags:
                    base_template = 'Critter'
                if 'BUILDABLE_OBJECT' in flags:
                    base_template = 'Buildable'
                print('{{'+base_template)
                print(f'| Name                = {name}')
                print(f'| Stack Size          = {stack_size}')
                if object_type != '':
                    print(f'| Type                = {object_type}')
                if len(object_size) == 3:
                    print(f'| Lenth               = {object_size["x"]}')
                    print(f'| Width               = {object_size["z"]}')
                    print(f'| Height              = {object_size["y"]}')
                if requires_foundation:
                    print(f'| Requires Foundation = 1')
                if fuel_value != '':
                    print(f'| Fuel Value = {fuel_value}')
                if lvg_connection:
                    print(f'| Low Voltage Grid    = 1')
                if 'CONSUMER' in power_subtype and energy_consumption != '' and energy_consumption != '0':
                    print(f'| Energy Consumption  = {energy_consumption}')
                if hvg_connection:
                    print(f'| High Voltage Grid        = 1')
                    print(f'| High Voltage Subtype     = {power_subtype}')
                    print(f'| High Voltage Connections = {hvg_connection_max}')
                    print(f'| High Voltage Range       = {hvg_connection_range}')
                if 'TRANSFORMER' in power_subtype and hvg_transmission != '' and hvg_transmission != '0':
                    print(f'| High Voltage Transmission = {hvg_transmission}')
                if 'SALES_ITEM' in flags:
                    print(f'| Sales Category      = {sales_categories[si_category]}')
                    print(f'| Sales Industry      = {industries[si_industry]}')
                    print(f'| Sales Price         = {si_price}')
                    print(f'| Sales Base Demand   = {si_base_demand}')
                if 'WORKSTATION_ITEM' in flags:
                    print(f'| Workstation Types   = {ws_types}')
                if 'BUILDABLE_OBJECT' in flags and len(ws_affects) > 0:
                    print(f'| Workstation Affects = {ws_affects}')
                    print(f'| Workstation Excludes = {ws_excludes}')
                if object_type == 'Producer':
                    print(f'| Production Multiplier = {producer_modifier}')
                print('}}')
                if has_recipe:
                    print('\n== Crafting ==')
                    for maker in made_in:
                        print(f'* {crafting_tags[maker]}')

                print('')
                if has_recipe:
                    print('[[Category:Craftable Objects]]')
                if 'BUILDABLE_OBJECT' in flags:
                    print('[[Category:Buildable Objects]]')
                if 'BURNABLE' in flags:
                    print('[[Category:Burnables]]')
                if 'CRITTER' in flags:
                    print('[[Category:Critters]]')
                if is_modular_building:
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
