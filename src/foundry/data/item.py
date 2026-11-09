"""Item template functions.

Copyright 2026 Stephen M. Webb  <stephen.webb@bregmasoft.ca>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path
from typing import LiteralString

import yaml
from mwparserfromhell.nodes import Template

from foundry.config import Config

from .buildable import Buildable
from .creative_mode import CreativeMode
from .industry import Industry
from .sales_category import SalesCategory
from .workstation_effect import WorkstationEffect

NAME_FIELD: LiteralString = 'name'
ID_FIELD: LiteralString = 'identifier'
FLAGS_FIELD: LiteralString = 'flags'
ICON_ID_FIELD: LiteralString = 'icon_identifier'
STACK_SIZE_FIELD: LiteralString = 'stackSize'
FUEL_VALUE_FIELD: LiteralString = 'burnable_fuelValueKJ_str'
CM_INCLUDE_FIELD: LiteralString = 'includeInCreativeMode'
CM_CATEGORY_FIELD: LiteralString = 'creativeModeCategory_str'
SALES_CATEGORY_FIELD: LiteralString = 'salesItem_salesItemCategoryIdentifier'
SALES_INDUSTRY_FIELD: LiteralString = 'salesItem_industryIdentifier'
SALES_PRICE_FIELD: LiteralString = 'salesItem_currencyAmount'
SALES_DEMAND_FIELD: LiteralString = 'salesItem_salesPlatformBaseDemandPerDay'
WS_DATA01_FIELD: LiteralString = 'workstationItem_data01'
WS_DATA02_FIELD: LiteralString = 'workstationItem_data02'
WS_REQUIRED_FIELD: LiteralString = 'workstationItem_requiredTags'
WS_EXCLUDED_FIELD: LiteralString = 'workstationItem_excludedTags'


class Item:
    """Class wrapping information on any instantiable item in the game."""

    creative_mode: CreativeMode = None
    industry: Industry = None
    sales_category: SalesCategory = None
    ws_effects: WorkstationEffect = None

    def __init__(self, item_file_path: Path, config: Config) -> None:
        """Initialize an Item from its template file.

        Parameters
        ----------
        item_file_path: Path
            Identifies the Item template file to load
        config: Config
            The application configuration

        """
        if Item.creative_mode is None:
            Item.creative_mode = CreativeMode(config)
        if Item.industry is None:
            Item.industry = Industry(config)
        if Item.sales_category is None:
            Item.sales_category = SalesCategory(config)
        if Item.ws_effects is None:
            Item.ws_effects = WorkstationEffect(config)

        with item_file_path.open() as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
            for v in yaml_data['ItemTemplate'].values():
                self.name                = v[NAME_FIELD]
                self.item_id             = v[ID_FIELD]
                self.flags               = v[FLAGS_FIELD]
                self.icon_id             = v[ICON_ID_FIELD]
                self.stack_size          = v[STACK_SIZE_FIELD]
                self.is_modular_building = False

                self.fuel_value          = v[FUEL_VALUE_FIELD]

                self.cm_in_creative_mode = v[CM_INCLUDE_FIELD]
                self.cm_category         = Item.creative_mode.id_to_name(v[CM_CATEGORY_FIELD])

                self.si_category         = Item.sales_category.id_to_name(v[SALES_CATEGORY_FIELD])
                self.si_industry         = Item.industry.id_to_name(v[SALES_INDUSTRY_FIELD])
                self.si_price            = v[SALES_PRICE_FIELD]
                self.si_base_demand      = v[SALES_DEMAND_FIELD]

                self.ws_data1            = v[WS_DATA01_FIELD]
                self.ws_data2            = v[WS_DATA02_FIELD]
                self.ws_required         = Item.ws_effects.translate_effects_list(v[WS_REQUIRED_FIELD])
                self.ws_excluded         = Item.ws_effects.translate_effects_list(v[WS_EXCLUDED_FIELD])
                self.buildable = None
                try:
                    self.buildable = Buildable(self.item_id, config)
                except FileNotFoundError:
                    if config.verbose:
                        print(f'failed to load Buildable for item_id {self.item_id}')

    def _put_buildable_info(self, infobox: Template) -> None:
        if self.buildable:
            if self.buildable.object_type != '':
                infobox.add('Type', self.buildable.object_type)
            if len(self.buildable.object_size) == 3:
                infobox.add('Lenth',  self.buildable.object_size["x"])
                infobox.add('Width',  self.buildable.object_size["z"])
                infobox.add('Height', self.buildable.object_size["y"])
            if self.buildable.requires_foundation:
                infobox.add('Requires Foundation', '1')
            if self.buildable.has_data_system:
                infobox.add('Data System Support', '1')
            if self.buildable.blast_resistant:
                infobox.add('Blast Resistant', '1')
            self._put_lvg_info(infobox)
            self._put_hvg_info(infobox)
            self._put_producer_info(infobox)
            self._put_transformer_info(infobox)
            self._put_battery_info(infobox)
            self._put_storage_info(infobox)

    def _put_producer_info(self, infobox: Template) -> None:
        if len(self.buildable.recipe_producer_types) > 0:
            infobox.add('Recipe Producer Types', self.buildable.recipe_producer_types)
            infobox.add('Recipe Multiplier', self.buildable.recipe_multiplier)

    def _put_lvg_info(self, infobox: Template) -> None:
        if self.buildable.lvg_connection:
            infobox.add('Low Voltage Grid', '1')
        if 'CONSUMER' in self.buildable.power_subtype and self.buildable.energy_consumption not in {'', '0'}:
            infobox.add('Energy Consumption', self.buildable.energy_consumption)

    def _put_hvg_info(self, infobox: Template) -> None:
        if self.buildable.hvg_connection:
            infobox.add('High Voltage Grid',        '1')
            infobox.add('High Voltage Subtype',     self.buildable.power_subtype)
            infobox.add('High Voltage Connections', self.buildable.hvg_connection_max)
            infobox.add('High Voltage Range',       self.buildable.hvg_connection_range)

    def _put_transformer_info(self, infobox: Template) -> None:
        if 'TRANSFORMER' in self.buildable.power_subtype and self.buildable.hvg_transmission not in {'', '0'}:
            infobox.add('High Voltage Transmission', self.buildable.hvg_transmission)

    def _put_battery_info(self, infobox: Template) -> None:
        if self.buildable.battery_capacity:
            infobox.add('Battery Capacity', self.buildable.battery_capacity)

    def _put_storage_info(self, infobox: Template) -> None:
        if self.buildable.storage_size:
            infobox.add('Storage Size', self.buildable.storage_size)

    def _put_sales_info(self, infobox: Template) -> None:
        if 'SALES_ITEM' in self.flags:
            infobox.add('Sales Category', self.si_category)
            infobox.add('Sales Industry', self.si_industry)
            infobox.add('Sales Price', self.si_price)
            infobox.add('Sales Base Demand', self.si_base_demand)

    def _put_workstation_info(self, infobox: Template) -> None:
        if 'WORKSTATION_ITEM' in self.flags:
            infobox.add('Workstation Targets', self.ws_required)
            infobox.add('Workstation Excludes', self.ws_excluded)
            if self.buildable and self.buildable.ws_affects:
                infobox.add('Workstation Affects', self.buildable.ws_affects)

    def wikitext_infobox(self) -> Template:
        """Create Infobox wikicode for this Item.

        Returns
        -------
        Template
            An MWPFH node containing the populated Infobox template for this Item.

        """
        def infobox_type(flags: str) -> Template:
            base_template = 'Item'
            if 'CRITTER' in flags:
                base_template = 'Critter'
            if 'BUILDABLE_OBJECT' in flags:
                base_template = 'Buildable'
            return base_template

        infobox = Template(f'{infobox_type(self.flags)}\n')

        infobox.add('Name', f' {self.name}\n')
        if self.stack_size > 0:
            infobox.add('Stack Size', self.stack_size)
        if self.fuel_value != '':
            infobox.add('Fuel Value', self.fuel_value)
        if self.cm_in_creative_mode and self.cm_category and len(self.cm_category) > 0:
            infobox.add('Category', self.cm_category)
        self._put_buildable_info(infobox)
        self._put_sales_info(infobox)
        self._put_workstation_info(infobox)
        return infobox

    @staticmethod
    def id_to_name(item_id: str, config: Config) -> str:
        """Map an item ID to an item name.

        Parameters
        ----------
        item_id: str
            Identifies the item IS to map
        config: Config
            The application configuration

        Returns
        -------
        str
            The name corresponding to `item_id` or an empty string if one
            was not found.

        """
        # Python equivalent of an initialize-on-first-use static variable
        if not hasattr(Item.id_to_name, 'name_map'):
            Item.id_to_name.name_map = Item._load_names(config)

        if item_id and item_id != '':
            return Item.id_to_name.name_map[item_id]
        return ''

    @staticmethod
    def _load_names(config: Config) -> dict[str, str]:
        """Load a map of item ID to item name.

        Internal static method used to initialize the ID-to-name mapping
        table used by the id_to_name() method. The table is created by
        scanning all the ItemTemplate yaml files and generating a dictionary
        to map each name to its ID.

        Parameters
        ----------
        config: Config
            The application configuration

        Returns
        -------
        dict[str, str]
            A mapping of item ID to item name

        """
        item_name = {}
        item_path = Path(config.template_base, 'ItemTemplate')
        for file_path in item_path.glob('*.yaml'):
            with file_path.open() as yaml_file:
                resource = yaml.safe_load(yaml_file)
                for v in resource['ItemTemplate'].values():
                    item_name[v[ID_FIELD]] = v[NAME_FIELD]
        return item_name
