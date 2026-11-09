"""Entry point for the command-line interface.

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

import click

from foundry.config.config import Config

from .list import list_cli


@click.group()
@click.option('-c', '--config',  type=click.File('r'), help='load site config from named file')
@click.option('-d', '--debug',   is_flag=True,         help='emit internal debugging diagnostics')
@click.option('-v', '--verbose', count=True,           help='increase logging verbosity')
@click.pass_context
def cli(ctx: click.Context, config: click.File, debug: click.INT, verbose: click.BOOL) -> None:
    """Mainline driver for the tool."""
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
