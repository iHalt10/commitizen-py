from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Type

from jinja2 import Template
from semver.version import Version

from .conventional_commits.commit_type import CommitType
from .defaults import format_tag
from .defaults import init_version_files

if TYPE_CHECKING:
    from cz.conventional_commits.message.footer import BaseFooter
    from cz.conventional_commits.message.footer import FooterPrefixType
    from cz.versioning import BaseVersionFile
    from cz.versioning import VersionAttributes

    from .question import Question

    FormatTagFunc = Callable[[Version], str]
    InitVersionFilesFunc = Callable[["CommitizenConfig"], list[BaseVersionFile]]


class CommitizenConfig:
    DEFAULT_REPOSITORY_PATH = Path.cwd()

    @classmethod
    def load(cls, repository_path: Path) -> "CommitizenConfig":
        config_file = Path(f"{repository_path}/.cz/config.py")
        local_data: dict[str, Any] = {}
        exec(compile(config_file.read_text(), config_file, "exec"), {}, local_data)
        config: CommitizenConfig = local_data["config"]
        config.set_repository_path(repository_path)
        return config

    def __init__(self) -> None:
        self.repository_path = self.DEFAULT_REPOSITORY_PATH
        self.repository_url = ""
        self.commit_types: dict[str, CommitType] = {}
        self.footer_classes: dict[FooterPrefixType, Type[BaseFooter]] = {}
        self.init_version_files_fn: InitVersionFilesFunc = init_version_files
        self.format_tag_fn: FormatTagFunc = format_tag
        self.titles: dict[CommitType, str] = {}
        self.bump_map: dict[CommitType, VersionAttributes] = {}
        self.questions: dict[str, Question] = {}

    def set_repository_path(self, path: Path | str) -> None:
        self.repository_path = Path(path) if isinstance(path, str) else path
        self.repository_path.resolve()

    @property
    def changelog_template(self) -> Template:
        if "_template" not in self.__dict__:
            s = Path(f"{self.repository_path}/.cz/CHANGELOG.j2").read_text()
            self._changelog_template = Template(s)
        return self._changelog_template

    def set_changelog_template(self, template: Template) -> None:
        self._changelog_template = template

    def set_repository_url(self, url: str) -> None:
        self.repository_url = url

    def set_init_version_files_fn(self, fn: InitVersionFilesFunc) -> None:
        self.init_version_files_fn = fn

    def set_format_tag_fn(self, fn: FormatTagFunc) -> None:
        self.format_tag_fn = fn

    def create_comit_type(self, name: str) -> CommitType:
        commit_type = self.commit_types.setdefault(name, CommitType(name))
        return commit_type

    def add_title(self, commit_type: CommitType, title: str) -> None:
        self.titles.setdefault(commit_type, title)

    def add_increment(
        self, commit_type: CommitType, increment: VersionAttributes
    ) -> None:
        self.bump_map[commit_type] = increment

    def add_footer_class(self, klass: Type[BaseFooter]) -> None:
        if "PREFIX" not in klass.__dict__:
            raise RuntimeError()
        self.footer_classes[klass.PREFIX] = klass
