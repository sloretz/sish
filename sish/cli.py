# PYTHON_ARGCOMPLETE_OK

import argcomplete
import argparse
import pathlib

from . import BindSpec
from .container import Container
from .workspace import Workspace


def main_sish():
    """Main entrypoint for  sish command."""
    _main_container_command('sish', 'open a shell into a container')


def main_rsish():
    """Main entrypoint for  rsish command."""
    _main_container_command('rsish', 'open a root shell into a container')


def _main_container_command(command_name, help_text):
    parser = argparse.ArgumentParser(description=help_text)
    parser.add_argument(
        'container', metavar='NAME', nargs='?',
        help='name of the container')

    # TODO(sloretz) auto complete of container name

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    ws = Workspace.find_nearest(pathlib.Path('.'))
    if ws is None:
        raise RuntimeError(f'You must call create-sish-container before {command_name} will work')

    if args.container is None:
        if len(ws.containers) != 1:
            raise RuntimeError(f'{command_name} needs a container name because this workspace has multiple of them')  # noqa
        container = ws.containers[0]
    else:
        container = ws.get_container(args.container)

    # Does not return
    container.exec_command(command_name)


def main_create_sish_container():
    """Main entrypoint for  create-sish-container command."""
    parser = argparse.ArgumentParser(
        description='tool for developing code in Apptainer containers')

    parser.add_argument(
        '--from', metavar='BUILD_SPEC', dest='from_', required=True,
        help='a definition file, path to a sandbox, ...')
    parser.add_argument(
        '--name', metavar='NAME', dest='name', required=True,
        help='name given to the container')
    parser.add_argument(
        '--bind', metavar='src[:dest[:opts]]', dest='binds', action='append',
        help='a path or bind path spec to make available in the container')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    binds = []
    if args.binds:
        for bind in args.binds:
            if ',' in bind:
                # Apptainer supports multiple bind specs separated by a comma
                # Allow that here too by splitting into multiple specs
                binds.extend(map(BindSpec.fromstr, bind.split(',')))
            else:
                binds.append(BindSpec.fromstr(bind))

    for bind in binds:
        if not pathlib.Path(bind.src).resolve().exists():
            raise ValueError(f'Bind source "{bind.src}" does not exist')

    ws = Workspace.find_nearest(pathlib.Path('.'))
    if ws is None:
        # create workspace since it doesn't exist yet
        ws = Workspace.create(pathlib.Path('.'))

    # Create a container in this workspace
    Container.create(args.name, ws.base_container_folder, args.from_, binds)
    print(f'Container "{args.name}" created successfully')
