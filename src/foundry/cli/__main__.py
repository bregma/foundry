""" Entry point for the command-line interface. """

import argparse as ARG
import configparser as CFG
import sys

from . import list

_commands = [
    list,
]

def get_config(args):
    """ Convert command-line arguments and config file into a global application configuration object."""
    config = CFG.ConfigParser()

    for key, value in vars(args).items():
        config.set("DEFAULT", key, str(value))

    if args.config:
        config.read(args.config.name)
    return config

def main(args=None):
    """ Command-line tool entry point."""
    if args is None:
        args = sys.argv[1:]

    parser = ARG.ArgumentParser(prog='hl')
    parser.add_argument("-c", "--config",
                        type=ARG.FileType('r'),
                        help="load site config from name file")
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="emit internal debugging diagnostics")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="increase logging verbosity")
    subparsers = parser.add_subparsers(title='commands')
    for command in _commands:
        command.add_parser(subparsers)

    args = parser.parse_args(args)
    config = get_config(args)
    try:
        args.func(config)
        sys.exit(0)
    except AttributeError:
        parser.print_help(sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
