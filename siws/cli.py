# PYTHON_ARGCOMPLETE_OK

import argcomplete
import argparse
import pathlib
import sys

from . import Action
from . import BindSpec
from . import find_dot_siws
from .config import Config
from .create import create_workspace


def cli_create_workspace(args):
    binds = []
    if args.binds:
        for bind in args.binds:
            if ',' in bind:
                # Singularity supports multiple bind specs separated by a comma
                # Allow that here too by splitting into multiple specs
                binds.extend(map(BindSpec.fromstr, bind.split(',')))
            else:
                binds.append(BindSpec(bind))

    for bind in binds:
        if not pathlib.Path(bind.src).resolve().exists():
            raise ValueError(f'Bind source "{bind.src}" does not exist')

    create_workspace(args.name, pathlib.Path(args.ws_path), args.from_, binds)


def cli_do_action(name, command):
    return lambda _: Action(name, command)()


def main():
    parser = argparse.ArgumentParser(description='tools for working with a singularity workspace')  # noqa
    subparsers = parser.add_subparsers()

    parser_create = subparsers.add_parser(
        'create', help='create a singularity workspace')
    parser_create.add_argument(
        '--name', metavar='NAME', default='container0',
        help='a name to give to the container (default: container0)')
    parser_create.add_argument(
        '--from', metavar='BUILD_SPEC', dest='from_', required=True,
        help='a singularity definition file, path to a sandbox, ...')
    parser_create.add_argument(
        '--bind', metavar='src[:dest[:opts]]', dest='binds', action='append',
        help='a path or bind path spec to make available in the container')
    parser_create.add_argument(
        'ws_path', metavar='PATH', action='store',
        help='the path to the siws workspace to create')
    parser_create.set_defaults(func=cli_create_workspace)

    ws_file = find_dot_siws()

    if ws_file:
        # Add commands from the .siws file
        config = Config(ws_file)
        for name, command in config.commands():
            parser_cmd = subparsers.add_parser(name, help=command)
            parser_cmd.set_defaults(func=cli_do_action(name, command))

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        sys.exit(parser.format_usage())

    args.func(args)
