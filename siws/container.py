import os
import pathlib
import shlex
import subprocess

from . import pretty_command
from .templates import get_template

class Container:

    @classmethod
    def create(cls, name, base_folder: pathlib.Path, from_, binds):
        """
        Create a new container in a workspace.

        :param name: the name of the container to create
        :param container_folder:
            a base path inside the workspace to create containers
        :param from_: a singularity build specification
        :param binds: binds to be used inside a container when spawning shells
        """
        # Make the container directory
        container_folder = base_folder / name
        if container_folder.exists():
            raise RuntimeError(f'Cannot create container with {name} because it already exists')  # noqa
        container_folder.mkdir()

        # create a _sandbox_ folder which the singularity sandbox will live
        sandbox_folder = container_folder / "_sandbox_"
        # create a commands/ folder for commands this container supports
        commands_folder = container_folder/ "commands"

        # Collect commands that will be run to create the container
        build_commands = []

        build_commands.append([
            'singularity',
            'build',
            '--fakeroot',
            '--sandbox',
            str(sandbox_folder),
            from_
        ])

        for bind in binds:
            destination = bind.dest
            if destination is None:
                destination = bind.src

            # resolve relative paths to absolute paths
            destination = str(pathlib.Path(destination).resolve())

            exec_command = [
                'singularity',
                'exec',
                '--fakeroot',
                '--writable',
                str(sandbox_folder),
                'mkdir',
                '-p',
                # TODO(sloretz) what does singularity do with relative paths in binds?
                destination
            ]
            build_commands.append(exec_command)

        # actually runs the commands
        for command in build_commands:
            print("Executing: ", pretty_command(command))
            subprocess.run(command, check=True)

        # Create files for commands this container will support
        commands_folder.mkdir()
        binds = '--bind ' + ','.join(map(str, binds))

        shell_template_args = {
            'binds': binds,
            'sandbox_folder': str(sandbox_folder),
        }
        shell_cmd = get_template('shell.in').substitute(shell_template_args)
        (commands_folder / 'sish').write_text(shell_cmd)

        rootshell_template_args = {
            'binds': binds,
            'sandbox_folder': str(sandbox_folder),
        }
        rootshell_cmd = get_template('rootshell.in').substitute(shell_template_args)
        (commands_folder / 'rsish').write_text(rootshell_cmd)

        return cls(container_folder)

    def __init__(self, container_folder: pathlib.Path):
        self._folder = container_folder.resolve()

    @property
    def name(self):
        return self._folder.name

    def exec_command(self, command_name):
        cmd_path = self._folder / 'commands' / command_name
        if not cmd_path.exists():
            raise RuntimeError(f'{self.name} does not support {command_name}')
        cmd, *args = shlex.split(cmd_path.read_text())
        os.execlp(cmd, cmd, *args)
