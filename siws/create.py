import pathlib
import shlex
import subprocess
import sys

from . import __version__
from . import get_template
from . import pretty_command
from .workspace import Workspace


def create_container(name, workspace: Workspace, from_, binds):
    container_folder = workspace.new_container_path().resolve()
    container_folder.mkdir()

    sandbox_folder = container_folder / "sandbox"
    create_log_path = container_folder / "create_log.txt"

    build_commands = []

    build_command = [
        'singularity',
        'build',
        '--fakeroot',
        '--sandbox',
        str(sandbox_folder),
        from_
    ]
    build_commands.append(build_command)

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

    # actually build
    for command in build_commands:
        print("Executing: ", pretty_command(command))
        subprocess.run(command, check=True)

    # Create command files for this container
    binds = '--bind ' + ','.join(map(str, binds))

    shell_template_args = {
        'binds': binds,
        'sandbox_folder': str(sandbox_folder),
    }
    shell_cmd = get_template('shell.in').substitute(shell_template_args)
    workspace.new_command('shell', shell_cmd)

    rootshell_template_args = {
        'binds': binds,
        'sandbox_folder': str(sandbox_folder),
    }
    rootshell_cmd = get_template('rootshell.in').substitute(shell_template_args)
    workspace.new_command('rootshell', rootshell_cmd)
