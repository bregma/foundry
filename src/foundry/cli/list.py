"""Subcommand to list entities.

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

import click
from mwparserfromhell.nodes import Template, Wikilink
from mwparserfromhell.wikicode import Wikicode

from foundry.config import Config
from foundry.data import Item


def find_icon(config: Config, icon_id: str) -> str:
    """Construct the icon file name and check its existence."""
    png_path = config["SOURCE"]["png_path"]
    png_file_name = Path(png_path, f'{icon_id}_512.png')
    print(f'--> looking for icon file "{png_file_name}"')
    return png_file_name if png_file_name.is_file() else ''


def align_template_equals(wikicode: Wikicode) -> Wikicode:
    """Aligns the '=' signs in all templates found in the given wikicode string."""
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


def list_command(config: Config) -> None:
    """Entry function for importer module."""
    template_directory = Path(config.template_base)
    if config.verbose:
        print(f'looking in "{template_directory}"')
    if not template_directory.is_dir():
        msg = f"Provided template path '{template_directory}' is not a valid directory."
        raise ValueError(msg)

    item_path = Path(template_directory, 'ItemTemplate')
    for file_path in item_path.glob('*.yaml'):
        item = Item(file_path, config)

        wikicode = Wikicode([])
        wikicode.append(item.wikitext_infobox())
        wikicode.append('\n\n')

        recipe_template = Template('Recipe/For Item')
        wikicode.append(recipe_template)
        wikicode.append('\n\n')
        if item.buildable is not None and item.buildable.is_modular_building:
            wikicode.append(Wikilink('Category:Modular Buildings'))
            wikicode.append('\n')
        if 'BURNABLE' in item.flags:
            wikicode.append(Wikilink('Category:Burnables'))
            wikicode.append('\n')
        if 'CRITTER' in item.flags:
            wikicode.append(Wikilink('Category:Critters'))
            wikicode.append('\n')
        if 'HANDHELD' in item.flags:
            wikicode.append(Wikilink('Category:Handhelds'))
            wikicode.append('\n')
        if 'SALES_ITEM' in item.flags:
            wikicode.append(Wikilink('Category:Sales Items'))
            wikicode.append('\n')
        if 'SEED' in item.flags:
            wikicode.append(Wikilink('Category:Seeds'))
            wikicode.append('\n')
        if 'WORKSTATION_ITEM' in item.flags:
            wikicode.append(Wikilink('Category:Workstation Items'))
            wikicode.append('\n')

        wiki_filename = f'{item.name.strip().replace(" ", "_")}.wiki'
        wiki_item_directory = config["OUTPUT"]["wiki_item_path"]
        outfile_name = Path(wiki_item_directory, wiki_filename)
        with outfile_name.open(mode='w') as outfile:
            print(str(align_template_equals(wikicode)), file=outfile)


@click.group("list")
@click.pass_obj
def list_cli(config: Config) -> None:
    """Main entry point for *list* command."""

@list_cli.command('item')
@click.option('-f', '--filter', 'filter_str', help='regex of objects to pass the filter')
@click.pass_obj
def translate_item(config: Config, filter_str: str) -> None:
    """Main entry point for the *list item* subcommand."""
    click.echo(f'--> filter="{filter}"')
    list_command(config)
