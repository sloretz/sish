import os
import pathlib
import shlex
from string import Template
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
                '--contain',
                '--fakeroot',
                '--writable',
                str(sandbox_folder),
                'mkdir',
                '-p',
                # TODO(sloretz) what does singularity do with relative paths in binds?
                destination
            ]
            build_commands.append(exec_command)

        # Create mount points for nvidia files that can't be mounted with a
        # writable container with --nv option
        # See https://github.com/hpcng/singularity/issues/5169
        extra_mount_points = [
            '/usr/bin/nvidia-smi',
            '/usr/bin/nvidia-debugdump',
            '/usr/bin/nvidia-persistenced',
            '/usr/bin/nvidia-cuda-mps-control',
            '/usr/bin/nvidia-cuda-mps-server',
            '/var/run/nvidia-persistenced/socket',
        ]
        for mount_point in extra_mount_points:
            # Create a directory if needed
            build_commands.append([
                'singularity',
                'exec',
                '--fakeroot',
                '--writable',
                str(sandbox_folder),
                'mkdir',
                '-p',
                str(pathlib.Path(mount_point).parent)
            ])
            # Touch the file
            build_commands.append([
                'singularity',
                'exec',
                '--fakeroot',
                '--writable',
                str(sandbox_folder),
                'touch',
                mount_point
            ])

        # actually runs the commands
        for command in build_commands:
            print("Executing: ", pretty_command(command))
            subprocess.run(command, check=True)

        # Create files for commands this container will support
        commands_folder.mkdir()
        if len(binds) > 0:
            binds = '--bind ' + ','.join(map(str, binds))
        else:
            binds = ''

        shell_template_args = {
            'binds': binds,
            'sandbox_folder': str(sandbox_folder),
            'container_name': name,
        }
        shell_cmd = get_template('shell.in').substitute(shell_template_args)
        (commands_folder / 'sish').write_text(shell_cmd)

        rootshell_template_args = {
            'binds': binds,
            'sandbox_folder': str(sandbox_folder),
            'container_name': name,
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
        template_str = cmd_path.read_text()
        args = {
            'cwd': pathlib.Path('.').resolve()
        }
        command = Template(template_str).substitute(args)
        cmd, *args = shlex.split(command)
        os.execlp(cmd, cmd, *args)
