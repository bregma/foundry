""" Subcommand to convert entities """

from fnmatch import fnmatch
import glob
import json
import os
import sys
import yaml


def add_parser(subparsers):
    """ Adds the CLI arguments parser for this subcommand. """
    parser = subparsers.add_parser('convert',
                                   help='convert entities (incomplete)')
    parser.add_argument('subcommand',
                        choices=['item', 'recipe', 'research'],
                        help="type of entity to load")
    parser.add_argument('filter',
                        nargs='?',
                        default='*',
                        help="name filter glob")
    parser.set_defaults(func=convert_command)


def convert_command(config):
    """ Entry function for importer module. """
    print(f'convert_command type={config["DEFAULT"]["subcommand"]} filter={config["DEFAULT"]["filter"]}')
    if config['DEFAULT']['subcommand'] == 'item':
        convert_item(config)

def convert_item(config):
    """ Convert an "item". """
    template_directory = config["SOURCE"]["template_path"]
    raw_item_directory = config['OUTPUT']['raw_item_path']
    item_path = os.path.join(template_directory, 'ItemTemplate')

    search_pattern = os.path.join(item_path, "*.yaml")
    for file_path in glob.iglob(search_pattern):
        with open(file_path, 'r') as yaml_file:
            resource = yaml.safe_load(yaml_file)
            for key, value in resource['ItemTemplate'].items():
                name = value['name']
                if fnmatch(name, config['DEFAULT']['filter']):
                    raw_item_path = os.path.join(raw_item_directory, name.replace(' ', '_')+'.json')
                    if config.verbose:
                        print(f'writing "{raw_item_path}"')
                    item = dict()
                    item["name"] = name
                    item["stack_size"] = value['stackSize']
                    item["flags"] = value['flags'].split(',')
                    item["icon"] = name+' (Item}' if value['icon_identifier'] else None

                    try:
                        with open(raw_item_path, mode='x') as raw_item_file:
                            json.dump(item, raw_item_file, indent=4)
                    except FileExistsError:
                        print(f'file "{raw_item_path}" exists, not overwriting', file=sys.stderr)
