from configparser import ConfigParser
from configparser import ExtendedInterpolation
import pathlib
from typing import Iterable
from typing import Optional
from typing import Tuple
from typing import TypeVar

from . import __version__
from . import get_template

from packaging.version import Version


WORKSPACE_FOLDER_NAME = '_siws_'


class IncompatibleVersion(Exception):
    pass


# For typing from class method python/typing#254
_Workspace = TypeVar('Workspace')


class Workspace:

    @classmethod
    def find_nearest(cls, path: pathlib.Path = pathlib.Path().absolute()) -> Optional[_Workspace]:
        """
        Given a path to a directory, return workspace in the closest ancestor including this one.
    
        Returns None if no path exists
        """
        if not path.is_dir():
            raise ValueError(f"expected a directory, but got '{path}'")

        path = path.resolve()

        siws_folder = path / WORKSPACE_FOLDER_NAME
        if siws_folder.exists():
            return cls(siws_folder)
        elif path.parents:
            return cls.find_nearest(path.parent)

    @classmethod
    def create(cls, ws_path):
        """Given a path with no siws workspace, create one."""
        siws_folder = ws_path / WORKSPACE_FOLDER_NAME
        if siws_folder.exists():
            raise RuntimeError(f'Cannot create workspace here because {siws_folder} already exists')  # noqa
    
        # Create _siws_/
        siws_folder.mkdir(parents=True)
    
        # Create _siws_/siws.ini
        ini_location = siws_folder / 'siws.ini'
        ini_content = get_template('siws.ini.in').substitute(siws_version=__version__)
        ini_location.write_text(ini_content)
    
        # Create _siws_/commands/
        commands_folder = siws_folder / 'commands'
        commands_folder.mkdir()
    
        # Create _siws_/containers/
        containers_folder = siws_folder / 'containers'
        containers_folder.mkdir()

        return cls(siws_folder)


    def __init__(self, siws_folder: pathlib.Path):
        self._siws_folder = siws_folder
        self._config = ConfigParser(interpolation=ExtendedInterpolation())
        self._config.read(siws_folder / 'siws.ini')

        self._compatible_version_check()

    def _compatible_version_check(self):
        tool_version = Version(__version__) 
        config_version = self.version

        # Initially, only compatible with same version
        if tool_version != config_version:
            raise IncompatibleVersion(f"{config_version} in {self._ws_dir} does not match CLI {tool_version}")  # noqa

    @property
    def version(self) -> Version:
        """Get the version of siws used to create this workspace."""
        return Version(self._config['siws']['version'])

    @property
    def location(self) -> pathlib.Path:
        """Get the path to the _siws_ folder."""
        return pathlib.Path(self._siws_folder)

    @property
    def containers(self) -> Tuple[pathlib.Path]:
        return tuple((self._siws_folder / 'containers').iterdir())

    @property
    def commands(self) -> Iterable[Tuple[str, str]]:
        for cmd_file in (self._siws_folder / 'commands').iterdir():
            yield str(cmd_file.name), cmd_file.read_text()

    def new_command(self, name, command):
        pathlib.Path(self._siws_folder / 'commands' / name).write_text(command)

    def new_container_path(self) -> pathlib.Path:
        """Return a unique path for a new container to live."""
        i = 0
        while True:
            new_path = self._siws_folder / 'containers' / ("container" + str(i))
            if not new_path.exists():
                return new_path
            i += 1
