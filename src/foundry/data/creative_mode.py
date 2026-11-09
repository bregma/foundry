"""CreativeMode template functions.

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

from foundry.config import Config

CREATIVE_MODE_TEMPLATE_NAME: LiteralString = 'CreativeModeCategoryTemplate'
CM_ID_FIELD: LiteralString = 'identifier'
CM_NAME_FIELD: LiteralString = 'categoryName'


class CreativeMode:
    """Stateful mapper between a Creative Mode Category ID and a creative mode category name."""

    name_mapping:dict[str, str] = None

    def __init__(self, config: Config) -> None:
        """Initialize a CreativeMode object.

        Really, this is a factory class and the only thing initialized is the class member
        `name_mapping`.

        """
        if CreativeMode.name_mapping is None:
            CreativeMode.name_mapping = CreativeMode._load_names(config)

    @staticmethod
    def _load_names(config: Config) -> dict[str, str]:
        """Load a map of creative mode tag ID to creative mode name.

        Generates a map from CreateMode ID to CreateMode name by parsing all
        the YAML files in the CreativeModeCategoryTemplate directory and
        creating a dict to map their ID field to their name field.

        Parameters
        ----------
        config: Config
            The application configuration

        """
        name_mapping = {}
        name_path = Path(config.template_base, CREATIVE_MODE_TEMPLATE_NAME)
        if config.verbose:
            print(f'.. loading sales industry name map from "{name_path}"')
        for file_path in name_path.glob('*.yaml'):
            with file_path.open() as yaml_file:
                resource = yaml.safe_load(yaml_file)
                for value in resource[CREATIVE_MODE_TEMPLATE_NAME].values():
                    name_mapping[value[CM_ID_FIELD]] = value[CM_NAME_FIELD]
        return name_mapping

    def id_to_name(self, category_id:str) -> str:
        """Map a creative mode ID to a creative mode name."""
        return CreativeMode.name_mapping[category_id] if category_id and category_id != '' else ''
