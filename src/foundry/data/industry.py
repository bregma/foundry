"""Industry template functions.

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

INDUSTRY_TEMPLATE_NAME: LiteralString = 'IndustryTemplate'
SI_ID_FIELD: LiteralString = 'identifier'
SI_NAME_FIELD: LiteralString = 'name'


class Industry:
    """Stateful mapper between a sales industry ID and a sales industry name."""

    name_mapping:dict[str, str] = None

    def __init__(self, config: Config) -> None:
        """Initialize a Industry object.

        Really, this is a factory class and the only thing initialized is the class member
        `name_mapping`.

        """
        if Industry.name_mapping is None:
            Industry.name_mapping = Industry._load_names(config)

    @staticmethod
    def _load_names(config: Config) -> dict[str, str]:
        """Load a map of sales industry tag ID to sales industry name.

        Parameters
        ----------
        config: Config
            The application configuration

        """
        name_mapping = {}
        name_path = Path(config.template_base, INDUSTRY_TEMPLATE_NAME)
        if config.verbose:
            print(f'.. loading sales industry name map from "{name_path}"')
        for file_path in name_path.glob('*.yaml'):
            with file_path.open() as yaml_file:
                resource = yaml.safe_load(yaml_file)
                for value in resource[INDUSTRY_TEMPLATE_NAME].values():
                    name_mapping[value[SI_ID_FIELD]] = value[SI_NAME_FIELD]
        return name_mapping

    def id_to_name(self, industry_id:str) -> str:
        """Map a sales industry ID to a sales industry name."""
        return Industry.name_mapping[industry_id] if (industry_id and industry_id != '') else ''
