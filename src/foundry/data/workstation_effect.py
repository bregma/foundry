"""Workstation Effects template functions.

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

WE_TEMPLATE_NAME: LiteralString = 'WorkstationEffectTagTemplate'
WE_ID_FIELD: LiteralString = 'identifier'
WE_NAME_FIELD: LiteralString = 'displayName'


class WorkstationEffect:
    """Stateful mapper between a workstation effect ID and a workstation effect name."""

    name_mapping:dict[str, str] = None

    def __init__(self, config: Config) -> None:
        """Initialize a CraftingTag object.

        Really, this is a factory class and the only thing initialized is the class member
        `tag_mapping`.

        Parameters
        ----------
        config: Config
            The application configuration

        """
        if WorkstationEffect.name_mapping is None:
            WorkstationEffect.name_mapping = WorkstationEffect._load_names(config)

    @staticmethod
    def _load_names(config: Config) -> dict[str, str]:
        """Load a map of workstation effect ID to workstation effect name.

        Parameters
        ----------
        config: Config
            The application configuration

        """
        name_mapping = {}
        name_path = Path(config.template_base, WE_TEMPLATE_NAME)
        if config.verbose:
            print(f'.. loading workstation effect name map from "{name_path}"')
        for file_path in name_path.glob('*.yaml'):
            with file_path.open() as yaml_file:
                resource = yaml.safe_load(yaml_file)
                for value in resource[WE_TEMPLATE_NAME].values():
                    name_mapping[value[WE_ID_FIELD]] = value[WE_NAME_FIELD]
        return name_mapping

    def id_to_name(self, we_id:str) -> str:
        """Map a workstation effect ID to a workstation effect name."""
        return WorkstationEffect.name_mapping[we_id]

    def translate_effects_list(self, aggregate: list[str]) -> str:
        """Translate a workstation effects from yaml to a CSV string.

        This trick is necessary because the YAML encodes the workstation targets as a
        vertical-bar-separated value list, where the target it_id is the first field.

        Parameters
        ----------
        aggregate: list[str]
            The YAML aggregate value (list) of workstation effect IDs in a coded format.
        config: Config
            The application configuration.

        Returns
        -------
            A comma-sepoarated value string of workstation effect names.

        """
        return ', '.join([self.id_to_name(s.split('|')[0]) for s in aggregate])
