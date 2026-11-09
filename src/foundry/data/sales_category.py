"""Sales Item Category template functions.

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

SC_TEMPLATE_NAME: LiteralString = 'SalesItemCategoryTemplate'
SC_ID_FIELD: LiteralString = 'identifier'
SC_NAME_FIELD: LiteralString = 'name'


class SalesCategory:
    """Stateful mapper between a sales category ID and a sales category name."""

    name_mapping:dict[str, str] = None

    def __init__(self, config: Config) -> None:
        """Initialize a SalesCategory object.

        Really, this is a factory class and the only thing initialized is the class member
        `tag_mapping`.

        Parameters
        ----------
        config: Config
            The application configuration

        """
        if SalesCategory.name_mapping is None:
            SalesCategory.name_mapping = SalesCategory._load_names(config)

    @staticmethod
    def _load_names(config: Config) -> dict[str, str]:
        """Load a map of sales category ID to sales category name.

        Parameters
        ----------
        config: Config
            The application configuration

        """
        name_mapping = {}
        name_path = Path(config.template_base, SC_TEMPLATE_NAME)
        if config.verbose:
            print(f'.. loading sales category name map from "{name_path}"')
        for file_path in name_path.glob('*.yaml'):
            with file_path.open() as yaml_file:
                resource = yaml.safe_load(yaml_file)
                for value in resource[SC_TEMPLATE_NAME].values():
                    name_mapping[value[SC_ID_FIELD]] = value[SC_NAME_FIELD]
        return name_mapping

    def id_to_name(self, sales_category_id:str) -> str:
        """Map a sales category ID to a sales category name."""
        def is_valid(sales_category_id:str) -> bool:
            return sales_category_id and sales_category_id != ''
        return SalesCategory.name_mapping[sales_category_id] if is_valid(sales_category_id) else ''
