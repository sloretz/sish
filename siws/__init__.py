import os
import pathlib
import shlex
from typing import Optional


# This file must ONLY import standard modules so that setup.py can import it
__version__ = "0.1.0"


def find_dot_siws(path: pathlib.Path = pathlib.Path().absolute()) -> Optional[pathlib.Path]:  # noqa
    """
    Given a path to a directory, return the path to a .siws file in the
    closest ancestor including this one.

    Returns None if no path exists
    """
    if not path.is_dir():
        raise ValueError(f"expected a directory, but got '{path}'")

    dot_path = path / '.siws'
    if dot_path.exists():
        return dot_path
    elif path.parents:
        return find_dot_siws(path.parent)


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

    def __init__(self, src, dest=None, opts=None):
        if opts:
            if not dest:
                raise ValueError(
                    'Bind specifications may only have opts if dest is given')
            allowed_opts = ('ro', 'rw')
            if opts not in allowed_opts:
                raise ValueError(
                    f'Bind specification opts must be one of {allowed_opts}')
        self.src = src
        self.dest = dest
        self.opts = opts

    @classmethod
    def fromstr(cls, spec_str):
        parts = spec_str.split(':')
        if len(parts) > 3:
            raise ValueError(
                'Bind specifications may not have more than 3 parts')
        return BindSpec(*parts)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__}({repr(self.src)}, {repr(self.dest)}, {repr(self.opts)})>'  # noqa

    def __str__(self):
        parts = [self.src, self.dest, self.opts]
        while parts[-1] is None:
            parts.pop()
        return ':'.join(parts)
