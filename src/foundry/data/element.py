"""Element template functions.

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

TEMPLATE_NAME: LiteralString = 'ElementTemplate'
NAME_FIELD: LiteralString = 'name'
ID_FIELD: LiteralString = 'identifier'

FUEL_FLAG: LiteralString = 'FUEL'


class Element:
    """Class wrapping information on any instantiable elemnt in the game."""

    config: Config = None

    def __init__(self, element_file_path: Path, config: Config) -> None:
        """Initialize an Element from its template file.

        Parameters
        ----------
        element_file_path: Path
            Identifies the Element template file to load
        config: Config
            The application configuration

        """
        if Element.config is None:
            Element.config = config

        with element_file_path.open() as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
            for v in yaml_data[TEMPLATE_NAME].values():
                self.name                 = v[NAME_FIELD]
                self.icon_identifier      = v['icon_identifier']
                self.flags                = v['flags']
                self.pipe_content_color   = v['pipeContentColor']
                self.pipe_content_type    = v['pipeContentType']
                self.fuel_value           = v['fuel_fuelValueKJPerL_str']
                self.fuel_residual_id     = v['fuel_residualTemplate_identifier']
                self.fuel_residual_amount = v['fuel_residualAmountPerL_str']
                self.fuel_flags           = v['fuel_flags']
                self.fuel_min             = v['fuel_minViableVolumeL_str']
                self.build_tags           = v['buildTags']

    @staticmethod
    def _load_names(config: Config) -> dict:
        print('loading elements...')
        elements = {}
        elements_path =  Path(config.template_base, TEMPLATE_NAME)
        for file_path in elements_path.glob('*.yaml'):
            with file_path.open() as yaml_file:
                resource = yaml.safe_load(yaml_file)
                for value in resource[TEMPLATE_NAME].values():
                    elements[value[ID_FIELD]] = value[NAME_FIELD]
        return elements

    @staticmethod
    def id_to_name(element_id: str) -> str:
        """Map an item ID to an element name.

        Parameters
        ----------
        element_id: str
            Identifies the item IS to map
        config: Config
            The application configuration

        Returns
        -------
        str
            The name corresponding to `element_id` or an empty string if one
            was not found.

        """
        # Python equivalent of an initialize-on-first-use static variable
        if not hasattr(Element.id_to_name, 'name_map'):
            Element.id_to_name.name_map = Element._load_names(Element.config)

        if element_id and element_id != '':
            return Element.id_to_name.name_map[element_id]
        return ''

    def wikitext_infobox(self) -> Template:
        """Create Infobox wikicode for this Element.

        Returns
        -------
        Template
            An MWPFH node containing the populated Infobox template for this Element.

        """
        infobox = Template('Element\n')
        infobox.add('Name', f' {self.name}\n')
        infobox.add('Color',
                     (f'rgba({self.pipe_content_color["r"]*255}, '
                      f'{self.pipe_content_color["g"]*255}, '
                      f'{self.pipe_content_color["b"]*255}, '
                      f'{self.pipe_content_color["a"]})\n'))
        if FUEL_FLAG in self.flags:
            infobox.add('Fuel Value', self.fuel_value)
            infobox.add('Fuel Min',   self.fuel_min)
            if len(self.fuel_residual_id):
                infobox.add('Fuel Residual Name',   self.id_to_name(self.fuel_residual_id))
                infobox.add('Fuel Residual Amount', self.fuel_residual_amount)
        return infobox

