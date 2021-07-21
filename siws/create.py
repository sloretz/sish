try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

import pathlib
import shlex
from string import Template
import subprocess


def create_workspace(from_, binds):
    print("TODO create workspace from", from_, "with binds", binds)
    # from_ will get passed to singularity build
    # from_ needs some parsing to come up with a sandbox name :-/
    # binds will have their destination created inside the container with 
    #   singularity exec
    # binds will be included in the ref:_shell

    template_path = files('siws.templates').joinpath('siws.in')
    print("Reading from template path", template_path)

    command = [
        'singularity',
        'build',
        '--fakeroot',
        '--sandbox',
        shlex.quote('TODO SANDBOX PATH WITH QUOTES'),
        shlex.quote(from_)
    ]
    print(" ".join(command))

    for bind in binds:
        destination = bind.dest
        if destination is None:
            destination = bind.src

        # resolve relative paths to absolute paths
        destination = str(pathlib.Path(destination).resolve())

        command = [
            'singularity',
            'exec',
            '--fakeroot',
            '--writable',
            shlex.quote('TODO SANDBOX PATH WITH QUOTES'),
            'mkdir',
            '-p',
            # hmm - need to assert dest is absolute path?
            shlex.quote(destination)
        ]
        print(" ".join(command))
