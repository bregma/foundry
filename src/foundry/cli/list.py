""" Subcommand to list entities """

import click
import glob
import os
import sys
import yaml
from ..config.config import Config
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Heading, Template, Wikilink

_item_name: dict
_crafting_tags: dict
_template_directory: str
_workstation_effects: dict


def load_item_names():
    item_name = {}
    item_path = os.path.join(_template_directory, 'ItemTemplate')
    search_pattern = os.path.join(item_path, '*.yaml')
    for file_path in glob.iglob(search_pattern):
        with open(file_path, 'r') as yaml_file:
            resource = yaml.safe_load(yaml_file)
            for key, value in resource['ItemTemplate'].items():
                item_name[value['identifier']] = value['name']
    return item_name


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
    """ Class wrapping info on a buildable item."""

    def __init__(self, item_id: str):
        buildable_object_path = os.path.join(_template_directory, 'BuildableObjectTemplate')
        buildable_obj_file_path = os.path.join(buildable_object_path, item_id) + ".yaml"
        with open(buildable_obj_file_path, 'r') as bf:
            buildable_yaml = yaml.safe_load(bf)
            buildable = buildable_yaml['BuildableObjectTemplate'][item_id]
            self.object_type             = buildable['type']
            self.object_size             = buildable['size']
            self.requires_foundation     = buildable['hasToBeOnFoundation']
            self.is_modular_building     = bool(buildable["isModularBuilding"])
            self.power_subtype           = buildable['powerSubType']
            self.energy_consumption      = buildable['energyConsumptionKW_str']
            self.lvg_connection          = bool(buildable['hasEnergyGridConnection'])
            self.hvg_connection          = bool(buildable['hasPoleGridConnection'])
            self.hvg_connection_max      = int(buildable['poleGrid_maxConnections'])
            self.hvg_connection_range    = int(buildable['poleGrid_connectionRange'])
            self.hvg_transmission        = buildable['transformer_transmissionRate_kjPerS_str']
            self.battery_capacity        = buildable['battery_capacityKJ_str']
            self.storage_size            = buildable['storage_slotSize']
            self.has_data_system         = bool(buildable['hasDataSystemManager'])
            self.blast_resistant         = not bool(buildable['canBeDestroyedByDynamite'])

            self.recipe_multiplier       = ''
            self.recipe_producer_types   = ''
            if self.object_type == 'Producer':
                self.recipe_multiplier     = str(buildable['producer_recipeTimeModifier_str'])
                self.recipe_producer_types = ', '.join([_crafting_tags[t] for t in buildable['producer_recipeType_tags']])
            elif self.object_type == 'AutoProducer':
                self.recipe_multiplier     = str(buildable['autoProducer_recipeTimeModifier_str'])
                self.recipe_producer_types = _crafting_tags[buildable['autoProducer_recipeType_tag']]
            elif self.object_type == 'ModularEntityProducer':
                self.recipe_multiplier     = str(buildable['modularProducer_recipeTimeModifier_str'])
                self.recipe_producer_types = ', '.join([_crafting_tags[t] for t in buildable['modularProducer_recipeType_tags']])
            self.ws_affects              = None

            if bool(buildable['hasWorkstationEffectManager']):
                ws_affects_list = []
                for s in buildable['workstationEffectTags']:
                    ws_affects_list.append(_workstation_effects[s.split('|')[0]])
                self.ws_affects       = ', '.join(ws_affects_list)

def align_template_equals(wikicode):
    """
    Aligns the '=' signs in all templates found in the given wikicode string.
    """
    for template in wikicode.filter_templates():
        # Get all parameter names and values
        params = [(str(p.name).strip(), str(p.value).strip()) for p in template.params]

        if not params:
            continue

        # Find the longest parameter name length
        max_name_len = max(len(name) for name, _ in params)

        # Rebuild the template text with aligned '='
        aligned_lines = []
        for name, value in params:
            padding = " " * (max_name_len - len(name))
            aligned_lines.append(f"| {name}{padding} = {value}")

        # Replace the template in the wikicode
        template_str = "{{" + str(template.name).strip() + "\n" + "\n".join(aligned_lines) + "\n}}"
        wikicode.replace(template, template_str)
    return wikicode


def list_command(config):
    """ Entry function for importer module. """
    global _item_name, _crafting_tags, _template_directory, _workstation_effects

    _template_directory = config["SOURCE"]["template_path"]
    if config.verbose:
        print(f'looking in "{_template_directory}"')
    if not os.path.isdir(_template_directory):
        raise ValueError(f"Provided template path '{_template_directory}' is not a valid directory.")

    _crafting_tags = load_crafting_tags(os.path.join(_template_directory, 'CraftingTag'))
    industries = load_industries(os.path.join(_template_directory, 'IndustryTemplate'))
    sales_categories = load_sales_categories(os.path.join(_template_directory, 'SalesItemCategoryTemplate'))
    _workstation_effects = load_workstation_effects()

    item_path = os.path.join(_template_directory, 'ItemTemplate')
    buildable_object_path = os.path.join(_template_directory, 'BuildableObjectTemplate')
    recipe_path = os.path.join(_template_directory, 'CraftingRecipe')
    research_path = os.path.join(_template_directory, 'ResearchTemplate')

    wiki_item_directory = config["OUTPUT"]["wiki_item_path"]
    _item_name = load_item_names()

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
                ws_required_list = []
                for s in value['workstationItem_requiredTags']:
                    ws_required_list.append(_workstation_effects[s.split('|')[0]])
                ws_required       = ', '.join(ws_required_list)
                ws_excluded_list = []
                for s in value['workstationItem_excludedTags']:
                    ws_excluded_list.append(_workstation_effects[s.split('|')[0]])
                ws_excluded       = ', '.join(ws_excluded_list)

                buildable = None
                try:
                    buildable = Buildable(item_id)
                except FileNotFoundError:
                    pass

                wiki_filename = f'{name.strip().replace(" ", "_")}.wiki'
                if config.verbose:
                    print(f'--> {name} : item_id="{item_id}" flags="{flags}" {"BUILDABLE" if buildable is not None else ""} {"IS_MODULAR" if is_modular_building else ""}')
                    print(f'--> file="{wiki_filename}"')

                wikicode = Wikicode([])

                base_template = 'Item'
                if 'CRITTER' in flags:
                    base_template = 'Critter'
                if 'BUILDABLE_OBJECT' in flags:
                    base_template = 'Buildable'
                infobox = Template(f'{base_template}\n')
                infobox.add('Name', f' {name}\n')
                if stack_size > 0:
                    infobox.add('Stack Size', stack_size)
                if fuel_value != '':
                    infobox.add('Fuel Value', fuel_value)
                if 'SALES_ITEM' in flags:
                    infobox.add('Sales Category    ', sales_categories[si_category])
                    infobox.add('Sales Industry    ', industries[si_industry])
                    infobox.add('Sales Price       ', si_price)
                    infobox.add('Sales Base Demand ', si_base_demand)
                if 'WORKSTATION_ITEM' in flags:
                    infobox.add('Workstation Targets', ws_required)
                    infobox.add('Workstation Excludes', ws_excluded)
                if buildable is not None:
                    if buildable.object_type != '':
                        infobox.add('Type                     ', buildable.object_type)
                    if len(buildable.object_size) == 3:
                        infobox.add('Lenth                    ', buildable.object_size["x"])
                        infobox.add('Width                    ', buildable.object_size["z"])
                        infobox.add('Height                   ', buildable.object_size["y"])
                    if buildable.requires_foundation:
                        infobox.add('Requires Foundation', '1')
                    if buildable.lvg_connection:
                        infobox.add('Low Voltage Grid', '1')
                    if 'CONSUMER' in buildable.power_subtype and buildable.energy_consumption != '' and buildable.energy_consumption != '0':
                        infobox.add('Energy Consumption', buildable.energy_consumption)
                    if buildable.hvg_connection:
                        infobox.add('High Voltage Grid', '1')
                        infobox.add('High Voltage Subtype', buildable.power_subtype)
                        infobox.add('High Voltage Connections', buildable.hvg_connection_max)
                        infobox.add('High Voltage Range', buildable.hvg_connection_range)
                    if 'TRANSFORMER' in buildable.power_subtype and buildable.hvg_transmission != '' and buildable.hvg_transmission != '0':
                        infobox.add('High Voltage Transmission', buildable.hvg_transmission)
                    if 'BUILDABLE_OBJECT' in flags:
                        if buildable.battery_capacity:
                            infobox.add('Battery Capacity', buildable.battery_capacity)
                        if buildable.storage_size:
                            infobox.add('Storage Size', buildable.storage_size)
                        if buildable.has_data_system:
                            infobox.add('Data System Support', '1')
                        if buildable.blast_resistant:
                            infobox.add('Blast Resistant', '1')
                        if buildable.ws_affects:
                            infobox.add('Workstation Affects', buildable.ws_affects)
                        if len(buildable.recipe_producer_types) > 0:
                            infobox.add('Recipe Producer Types', buildable.recipe_producer_types)
                            infobox.add('Recipe Multiplier', buildable.recipe_multiplier)
                wikicode.append(infobox)
                wikicode.append('\n\n')

                recipe_template = Template(f'Recipe/For Item')
                wikicode.append(recipe_template)
                wikicode.append('\n')
                wikicode.append('\n')
                if buildable is not None:
                    if buildable.is_modular_building:
                        wikicode.append(Wikilink('Category:Modular Buildings'))
                        wikicode.append('\n')
                if 'BURNABLE' in flags:
                    wikicode.append(Wikilink('Category:Burnables'))
                    wikicode.append('\n')
                if 'CRITTER' in flags:
                    wikicode.append(Wikilink('Category:Critters'))
                    wikicode.append('\n')
                if 'HANDHELD' in flags:
                    wikicode.append(Wikilink('Category:Handhelds'))
                    wikicode.append('\n')
                if 'SALES_ITEM' in flags:
                    wikicode.append(Wikilink('Category:Sales Items'))
                    wikicode.append('\n')
                if 'SEED' in flags:
                    wikicode.append(Wikilink('Category:Seeds'))
                    wikicode.append('\n')
                if 'WORKSTATION_ITEM' in flags:
                    wikicode.append(Wikilink('Category:Workstation Items'))
                    wikicode.append('\n')

                outfile_name = os.path.join('/home/stephen/projects/foundry/wiki/Main', wiki_filename)
                with open(outfile_name, 'w') as outfile:
                    print(str(align_template_equals(wikicode)), file=outfile)


@click.command("list")
@click.pass_obj
def list_cli(config):
    list_command(config)
