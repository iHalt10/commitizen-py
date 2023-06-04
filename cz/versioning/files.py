from abc import ABC
from abc import abstractmethod
from pathlib import Path

from semver.version import Version


class BaseVersionFile(ABC):
    IS_COMMIT = True

    @abstractmethod
    def get_path(self) -> Path:
        pass

    @abstractmethod
    def get_version(self) -> str:
        pass

    @abstractmethod
    def set_version(self, version: str) -> None:
        pass

    @abstractmethod
    def save(self) -> None:
        pass


class VersionFiles:
    def __init__(self, files: list[BaseVersionFile]) -> None:
        self.version_files = files

    def get_version(self) -> Version:
        version = self.validate(self.version_files[0])
        for version_file in self.version_files[1:]:
            if version != self.validate(version_file):
                raise RuntimeError()
        return version

    def validate(self, version_file: BaseVersionFile) -> Version:
        version_string = version_file.get_version()
        if not Version.isvalid(version_string):
            raise RuntimeError(f"not version format [{version_file.__class__.__name__}]")
        return Version.parse(version_string)

    def set_version(self, version: Version) -> None:
        for version_file in self.version_files:
            version_file.set_version(f"{version}")
            version_file.save()
