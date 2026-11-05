""" Entry point for the command-line interface. """

import click
import configparser as CFG
import sys

#from . import convert, index, list
from ..config.config import Config
from .list import list_cli


@click.group()
@click.option('-c', '--config',  type=click.File('r'), help='load site config from named file')
@click.option('-d', '--debug',   is_flag=True,         help='emit internal debugging diagnostics')
@click.option('-v', '--verbose', is_flag=True,         help='increase logging verbosity')
@click.pass_context
def cli(ctx, config, debug, verbose):
    """ """
    class Args:
        pass

    args = Args()
    args.config = config
    args.debug = debug
    args.verbose = verbose

    ctx.obj = Config.load(args)


cli.add_command(list_cli)


if __name__ == '__main__':
    cli()
