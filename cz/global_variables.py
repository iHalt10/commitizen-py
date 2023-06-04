from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .conventional_commits.commit import ConventionalCommit
    from .conventional_commits.commit_group import CommitGroup
    from .conventional_commits.tag import Tag
    from .conventional_commits.version_group import VersionGroup


class GlobalVariables:
    def __init__(self) -> None:
        self.commits: dict[str, ConventionalCommit] = {}
        self.tags: dict[str, Tag] = {}
        self.commit_groups: dict[str, CommitGroup] = {}
        self.version_groups: dict[Tag, VersionGroup] = {}
