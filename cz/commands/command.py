from pathlib import Path
from typing import Optional

from cleo.commands.command import Command

from cz.api.cz import CommitizenAPI
from cz.config import CommitizenConfig


class BaseCommand(Command):
    def __init__(self) -> None:
        super().__init__()
        self._config: Optional[CommitizenConfig] = None
        self._api: Optional[CommitizenAPI] = None

    @property
    def config(self) -> CommitizenConfig:
        if self._config is None:
            repository_path_string: Optional[str] = self.option("repository_path")
            repository_path = (
                Path(repository_path_string)
                if repository_path_string
                else CommitizenConfig.DEFAULT_REPOSITORY_PATH
            )
            self._config = CommitizenConfig.load(repository_path)

        return self._config

    @property
    def api(self) -> CommitizenAPI:
        if self._api is None:
            self._api = CommitizenAPI(self.config)
        return self._api
