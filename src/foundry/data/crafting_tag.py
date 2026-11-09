"""CraftingTag template functions.

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

CT_TEMPLATE_NAME: LiteralString = 'CraftingTag'
CT_ID_FIELD: LiteralString = 'identifier'
CT_NAME_FIELD: LiteralString = 'name'


class CraftingTag:
    """Stateful mapper between a crafting tag ID and a crafting tag name."""

    tag_mapping:dict[str, str] = None

    def __init__(self, config: Config) -> None:
        """Initialize a CraftingTag object.

        Really, this is a factory class and the only thing initialized is the class member
        `tag_mapping`.

        """
        if CraftingTag.tag_mapping is None:
            CraftingTag.tag_mapping = CraftingTag._load_crafting_tags(config)

    @staticmethod
    def _load_crafting_tags(config: Config) -> dict[str, str]:
        """Load a map of crafting tag ID to crafting tag name.

        Parameters
        ----------
        config: Config
            The application configuration

        """
        tag_mapping = {}
        tag_path = Path(config.template_base, CT_TEMPLATE_NAME)
        if config.verbose:
            print(f'.. loading crafting tag name map from "{tag_path}"')
        for file_path in tag_path.glob('*.yaml'):
            with file_path.open() as yaml_file:
                resource = yaml.safe_load(yaml_file)
                for value in resource[CT_TEMPLATE_NAME].values():
                    tag_mapping[value[CT_ID_FIELD]] = value[CT_NAME_FIELD]
        return tag_mapping

    def id_to_name(self, tag_id:str) -> str:
        """Map a crafting tag ID to a crafting tag name."""
        return CraftingTag.tag_mapping[tag_id]
