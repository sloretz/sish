import os
import pathlib
import shlex
from typing import Optional


# This file must ONLY import standard modules so that setup.py can import it
__version__ = "0.1.0"


def find_dot_singws(path : pathlib.Path) -> Optional[pathlib.Path]:
    """
    Given a path to a directory, return the path to a .singws file in the
    closest ancestor including this one.

    Returns None if no path exists
    """
    if not path.is_dir():
        raise ValueError(f"expected a directory, but got '{path}'")

    dot_path = path / '.singws'
    if dot_path.exists():
        return dot_path
    elif path.parents:
        return find_dot_singws(path.parent)


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


def create_workspace(from_):
    print("TODO create workspace from", from_)
