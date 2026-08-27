""" Subcommand to list entities """

import sys


def add_parser(subparsers):
    """ Adds the CLI arguments parser for this subcommand. """
    parser = subparsers.add_parser('list',
                                   help='list entities (incomplete)')
    parser.set_defaults(func=list_command)


def list_command(args):
    """ Entry function for importer module. """
    print(f'list command args={args}')
    args.write(sys.stdout)
