# pyright: reportUnknownVariableType=false
from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

import questionary
from semver.version import Version
from tomlkit import dumps
from tomlkit import parse

from cz.conventional_commits.message.footer import AllFooterLinesType
from cz.conventional_commits.message.footer import BaseFooter
from cz.versioning import BaseVersionFile

if TYPE_CHECKING:
    from cz.config import CommitizenConfig
    from cz.conventional_commits.message.message import Message
    from cz.question import QuestionPatternB


class BreakingChangeFooter(BaseFooter):
    PREFIX = "BREAKING CHANGE"
    MULTIPLE_MAX: int = 1
    LINES_MAX = 0

    @classmethod
    def ask(cls, message: Message, question: QuestionPatternB) -> None:
        if message.is_breaking:
            note: str = questionary.text(question["subject"], multiline=True).ask()
            note = re.sub(r"\n\n+", "\n", note)
            note = note.rstrip()
            note_lines = note.split("\n")
            note_lines[0]
            if len(note_lines) == 0:
                return
            elif len(note_lines) == 1:
                note_lines[0] = f"{cls.PREFIX}: {note_lines[0]}"
            else:
                note_lines.insert(0, f"{cls.PREFIX}:")
            footer = cls(message, {cls.PREFIX: [note_lines]})
            message.footer[cls.PREFIX] = footer

    def validete_footer(self, message: Message, footer: AllFooterLinesType) -> None:
        breaking_change_lines = footer[self.PREFIX][0]
        if not message.is_breaking:
            raise ValueError("flgを立ててください")
        if len(breaking_change_lines) == 1:
            if breaking_change_lines[0][len(self.PREFIX) + 1] != " ":
                raise ValueError("1行で書く場合は、spaceを開けて")
            breaking_change_lines[0] = breaking_change_lines[0].strip(f"{self.PREFIX}: ")
            self.body = "\n".join(breaking_change_lines)
        else:
            if breaking_change_lines[0] != f"{self.PREFIX}:":
                raise ValueError("複数行で書く場合は、1行目Prefixだけ")
            self.body = "\n".join(breaking_change_lines[1:])
        self.raw = "\n".join(breaking_change_lines)

    def __str__(self) -> str:
        return self.raw


class RevertHashFooter(BaseFooter):
    PREFIX = "Revert Hash"
    REVERT_HASH_REGEX = re.compile(r"^Revert Hash: (?P<hash>[0-9a-f]{40})")
    MULTIPLE_MAX = 1
    LINES_MAX = 1

    @classmethod
    def ask(cls, message: Message, question: Any) -> None:
        pass

    def validete_footer(self, message: Message, footer: AllFooterLinesType) -> None:
        if message.commit_type.name != "revert":
            raise ValueError("only revert footer revert type")
        revert_hash_line = footer[self.PREFIX][0][0]
        result = self.REVERT_HASH_REGEX.fullmatch(revert_hash_line)
        if not result:
            raise ValueError("not revert_hash_line format")
        self.hash = result.group("hash")
        self.raw = revert_hash_line

    def __str__(self) -> str:
        return self.raw


class ClosesFooter(BaseFooter):
    PREFIX = "Closes"
    CLOSES_REGEX = re.compile(r"^Closes: #\d+(, #\d+)*")
    MULTIPLE_MAX = 1
    LINES_MAX = 1

    @classmethod
    def ask(cls, message: Message, question: QuestionPatternB) -> None:
        closes: set[int] = set()
        while True:
            close_string: str = questionary.text(question["subject"]).ask()
            if not close_string.isdigit():
                break
            closes.add(int(close_string))
        if closes:
            closes_list = list(closes)
            closes_list.sort()
            closes_string = f"#{closes_list[0]}"
            for close in closes_list[1:]:
                closes_string = f"{closes_string}, #{close}"
            closes_string = f"{cls.PREFIX}: {closes_string}"
            footer = cls(message, {cls.PREFIX: [[closes_string]]})
            message.footer[cls.PREFIX] = footer

    def validete_footer(self, message: Message, footer: AllFooterLinesType) -> None:
        closes_line = footer[self.PREFIX][0][0]
        if not self.CLOSES_REGEX.fullmatch(closes_line):
            raise ValueError("not format")
        self.closes: list[int] = []
        for close in closes_line.strip(f"{self.PREFIX}: ").split(", "):
            self.closes.append(int(close.strip("#")))
        self.raw = closes_line

    def to_markdown(self, url: str) -> str:
        result = f"[#{self.closes[0]}]({url}/issues/{self.closes[0]})"
        for close_id in self.closes[1:]:
            result = f"{result}, [#{close_id}]({url}/issues/{close_id})"
        return result

    def __str__(self) -> str:
        return self.raw


class PyProjectTOML(BaseVersionFile):
    def __init__(self, path: Path | str = Path.cwd()) -> None:
        self.PATH = Path(f"{path}/pyproject.toml")
        self._data = parse(self.PATH.read_text())
        self.name = cast(str, self._data["tool"]["poetry"]["name"])  # type: ignore

    def get_path(self) -> Path:
        return self.PATH

    def get_version(self) -> str:
        return self._data["tool"]["poetry"]["version"]  # type: ignore

    def set_version(self, version: str) -> None:
        self._data["tool"]["poetry"]["version"] = version  # type: ignore

    def save(self) -> None:
        self.PATH.write_text(dumps(self._data))


class ModuleVersionFile(BaseVersionFile):
    PACKAGE_VERSION_REGEX = re.compile(r'^__version__ = "(?P<version>.+)"')

    def __init__(self, module_path: str) -> None:
        self.PATH = Path(f"{module_path}/__version__.py")
        text = self.PATH.read_text().split("\n")[0]
        result = self.PACKAGE_VERSION_REGEX.fullmatch(text)
        if not result:
            raise RuntimeError(f"__version__ not in {self.PATH}")
        self._version: str = result.group("version")

    def get_path(self) -> Path:
        return self.PATH

    def get_version(self) -> str:
        return self._version

    def set_version(self, version: str) -> None:
        self._version = version

    def save(self) -> None:
        self.PATH.write_text(f'__version__ = "{self._version}"\n')


def format_tag(next_version: Version) -> str:
    return f"{next_version}"


def init_version_files(config: CommitizenConfig) -> list[BaseVersionFile]:
    files: list[BaseVersionFile] = []
    pyproject = PyProjectTOML(config.repository_path)
    files.append(pyproject)
    files.append(ModuleVersionFile(f"{config.repository_path}/{pyproject.name}"))
    return files
