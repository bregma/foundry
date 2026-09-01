""" Subcommand to index entities """

import glob
import json
import os
import yaml


def add_parser(subparsers):
    """ Adds the CLI arguments parser for this subcommand. """
    parser = subparsers.add_parser('index',
                                   help='index entities (incomplete)')
    parser.add_argument('subcommand',
                        choices=['generate', 'diff'],
                        help="action to perform on the index file")
    parser.set_defaults(func=index_command)


def index_command(config):
    """ Entry function for importer module. """
    if config['DEFAULT']['subcommand'] == 'generate':
        index_generate(config)
    else:
        print(f'{config["DEFAULT"]["subcommand"]} is not yet available.')


def index_generate(config):
    """ Generate an index of all named and identified raws. """
    template_directory = config["SOURCE"]["template_path"]
    raw_index_directory = config['OUTPUT']['raw_index_path']
    index_table = {}

    search_pattern = os.path.join('*', '*.yaml')
    for file_path in glob.iglob(search_pattern, root_dir=template_directory, recursive=True):
        full_file_path = os.path.join(template_directory, file_path)
        try:
            with open(full_file_path, 'r', encoding='utf-8') as yaml_file:
                template = yaml.safe_load(yaml_file)
                for category, detail in template.items():
                    if category not in index_table:
                        index_table[category] = []
                    for _, value in detail.items():
                        try:
                            if len(str(value['name'])) > 0:
                                entry = {'name': value['name'], 'identifier': value['identifier']}
                                index_table[category].append(entry)
                        except KeyError:
                            continue
        except yaml.scanner.ScannerError:
            continue

    raw_index_path = os.path.join(raw_index_directory, 'raw_index.json')
    with open(raw_index_path, mode='x', encoding='utf-8') as raw_index_file:
        json.dump(index_table, raw_index_file, indent=4)
