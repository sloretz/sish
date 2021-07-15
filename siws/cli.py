# PYTHON_ARGCOMPLETE_OK

import argcomplete
import argparse
import pathlib
import sys

from . import Action
from . import create_workspace
from . import find_dot_siws
from .config import Config


def cli_create_workspace(args):
    create_workspace(args.from_)


def cli_make_action(name, command):
    return lambda _: Action(name, command)()


def main():
    parser = argparse.ArgumentParser(description='tools for working with a singularity workspace')  # noqa
    subparsers = parser.add_subparsers()

    parser_create = subparsers.add_parser(
        'create', help='create a singularity workspace')
    parser_create.add_argument(
        '--from', metavar='BUILD SPEC', dest='from_', required=True,
        help='a singularity definition file, path to a sandbox, ...')
    parser_create.set_defaults(func=cli_create_workspace)

    ws_file = find_dot_siws(pathlib.Path().absolute())

    if ws_file:
        # Add commands from the .siws file
        config = Config(ws_file)
        for name, command in config.commands():
            parser_cmd = subparsers.add_parser(name, help=command)
            parser_cmd.set_defaults(func=cli_make_action(name, command))

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        sys.exit(parser.format_usage())

    args.func(args)
