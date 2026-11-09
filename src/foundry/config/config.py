"""Application-wide configuration.

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
from __future__ import annotations

from configparser import ConfigParser


class Config(ConfigParser):
    """Application-wide configuration."""

    @classmethod
    def load(cls: Config, cli_args) -> Config:
        """Convert command-line arguments and config file into an application configuration object."""
        config = cls()

        for key, value in vars(cli_args).items():
            config.set("DEFAULT", key, str(value))

        if cli_args.config:
            config.read(cli_args.config.name)
        return config

    @property
    def verbose(self) -> int:
        """Indicate if verbose mode is enabled."""
        return self['DEFAULT'].getint('verbose')

    @property
    def template_base(self) -> str:
        """Gets the base path to the game templates.

        These templates are shipped with the game and are available as raw text files.
        """
        return self["SOURCE"]["template_path"]

