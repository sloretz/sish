from configparser import ConfigParser
from configparser import ExtendedInterpolation
import pathlib
from typing import Iterable
from typing import Tuple

from . import __version__

from packaging.version import Version


class IncompatibleVersion(Exception):
    pass


class Config:

    def __init__(self, ws_file_path):
        self._ws_dir = ws_file_path.parent
        self._config = ConfigParser(interpolation=ExtendedInterpolation())
        self._config.read(ws_file_path)

        self._compatible_version_check()

    def _compatible_version_check(self):
        tool_version = Version(__version__) 
        config_version = self.version

        # Initially, only compatible with same version
        if tool_version != config_version:
            raise IncompatibleVersion(f"{config_version} in {self._ws_dir} does not match CLI {tool_version}")  # noqa

    @property
    def version(self) -> Version:
        return Version(self._config['singws']['version'])

    @property
    def path(self) -> pathlib.Path:
        return pathlib.Path(self._config['singws']['path'])

    @property
    def container(self):
        return self._config['singws']['container']

    def commands(self) -> Iterable[Tuple[str, str]]:
        for name, cmd in self._config['commands'].items():
            yield (name, cmd)
