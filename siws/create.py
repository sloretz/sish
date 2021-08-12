try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

import pathlib
import shlex
from string import Template
import subprocess

from . import __version__
from . import container_path
from . import WORKSPACE_FOLDER_NAME


def execute_and_log(command, log_file_base):
    """
    Execute a command and output the results to
    log_file_base + '.stdout' and log_file_base + '.stderr'
    """
    results = subprocess.run(
        command,
        stdout=open(log_file_base + '.stdout', 'w'),
        stderr=open(log_file_base + '.stderr', 'w'),
        check=True)


def pretty_cmd(command):
    return " ".join(map(shlex.quote, command))


def create_workspace(name, ws_path, from_, binds):
    siws_folder = ws_path / WORKSPACE_FOLDER_NAME
    if siws_folder.exists():
        # TODO(sloretz) allow extending a .siws with multiple containers
        raise RuntimeError(f'Cannot create container here because {siws_folder} already exists')  # noqa

    container_folder = container_path(siws_folder, name)
    build_commands = []

    sandbox_path = str(siws_folder.joinpath(name + '.sandbox'))

    build_command = [
        'singularity',
        'build',
        '--fakeroot',
        '--sandbox',
        str(container_folder.resolve()),
        from_
    ]
    print(pretty_cmd(build_command))
    build_commands.append(build_command)
    # TODO(sloretz) uncomment this when ready :)
    # TODO(sloretz) pick better log output spot
    # execute_and_log(build_command, '/tmp/' + name)

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
            sandbox_path,
            'mkdir',
            '-p',
            # TODO(sloretz) what does singularity do with relative paths in binds?
            destination
        ]
        build_commands.append(exec_command)
        print(pretty_cmd(exec_command))
        # TODO(sloretz) uncomment when ready :)
        # subprocess.run(exec_command, check=True)

    # Now write the config file!

    tmp_commands = []
    for cmd in build_commands:
        tmp_commands.append("#   " + pretty_cmd(cmd))
    build_commands = tmp_commands
    del tmp_commands

    paths_template_args = {
        'container_name': name,
        'container_path': str(container_folder.resolve())
    }
    print(paths_template_args)
    paths_template = Template(files('siws.templates').joinpath('container_paths.in'))  # noqa
    print(paths_template.substitute(paths_template_args))

    commands_template_args = {
        'container_name': name
    }
    commands_template = Template(files('siws.templates').joinpath('container_commands.in'))  # noqa

    main_template_args = {
        'siws_version': __version__,
        'workspace_path': str(ws_path.resolve()),
        'container_paths': paths_template.substitute(paths_template_args),
        'comment_build_commands': "\n".join(build_commands),
        'binds': '--bind ' + ','.join(map(str, binds)),
        'container_commands': commands_template.substitute(command_template_args)
    }
    print(main_template_args)

    main_template = Template(files('siws.templates').joinpath('siws.in'))
    print(main_template.substitute(main_template_args))

