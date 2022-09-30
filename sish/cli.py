# PYTHON_ARGCOMPLETE_OK

import argcomplete
import argparse
import pathlib
import sys

from . import BindSpec
from .container import Container
from .workspace import Workspace


class UsageError(RuntimeError):
    pass


def main_sish():
    """Main entrypoint for  sish command."""
    return _main_container_command('sish', 'open a shell into a container')


def main_rsish():
    """Main entrypoint for  rsish command."""
    return _main_container_command('rsish', 'open a root shell into a container')


def _which_container(choices) -> str:
    if len(choices) == 1:
        return choices[0]

    which = None
    while which not in range(len(choices)):
        print('Which container?')
        for i, container in enumerate(choices):
            print(f' {i}: {container.name}')
        which_str = input('(0): ').strip()
        if len(which_str) == 0:
            which = 0
            break
        try:
            which = int(which_str)
        except ValueError:
            print("Invalid option", file=sys.stderr)

    return choices[which]


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
        print(f'No sish workspace here - create one with create-sish-container first', file=sys.stderr)
        return 1

    if args.container is None:
        container = _which_container(ws.containers)
    else:
        possible_containers = []
        for pc in ws.containers:
            if pc.name.startswith(args.container):
                possible_containers.append(pc)
        if not possible_containers:
            print(f'No container starts with text: {args.container}', file=sys.stderr)
            return 1

        container = _which_container(possible_containers)
        print(f"{command_name}: {args.container} -> {container.name}")

    if container is None:
        print(f'No such container: {args.container}', file=sys.stderr)
        return 1

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
