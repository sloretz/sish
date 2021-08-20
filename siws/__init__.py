try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

import os
import pathlib
import shlex
from string import Template
from typing import Optional


# This file must ONLY import standard modules so that setup.py can import it
__version__ = "0.1.0"


def get_template(name):
    template_folder = files('siws.templates')
    template_path = template_folder.joinpath(name)
    return Template(template_path.read_text())


def pretty_command(command):
    return " ".join(map(shlex.quote, command))


class Action:

    __slots__ = ['name', 'command']

    def __init__(self, name, command):
        self.name = name
        self.command = command

    def __call__(self):
        """
        Execute the action, replacing the current process.
    
        This function does not return.
        """
        cmd, *args = shlex.split(self.command)
        os.execlp(cmd, cmd, *args)


class BindSpec:

    __slots__ = ['src', 'dest', 'opts']

    def __init__(self, src: pathlib.Path, dest: Optional[pathlib.Path] = None, opts=None):
        if opts:
            if not dest:
                raise ValueError(
                    'Bind specifications may only have opts if dest is given')
            allowed_opts = ('ro', 'rw')
            if opts not in allowed_opts:
                raise ValueError(
                    f'Bind specification opts must be one of {allowed_opts}')
        self.src = src.resolve()
        self.dest = dest if dest is None else dest.resolve()
        self.opts = opts

    @classmethod
    def fromstr(cls, spec_str):
        parts = spec_str.split(':')
        if len(parts) > 3:
            raise ValueError(
                'Bind specifications may not have more than 3 parts')
        # src is a path
        parts[0] = pathlib.Path(parts[0])
        if len(parts) > 1:
            # dest is a path
            parts[1] = pathlib.Path(parts[1])
        return BindSpec(*parts)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__}({repr(self.src)}, {repr(self.dest)}, {repr(self.opts)})>'  # noqa

    def __str__(self):
        parts = [self.src, self.dest, self.opts]
        while parts[-1] is None:
            parts.pop()
        return ':'.join([str(p) for p in parts])
