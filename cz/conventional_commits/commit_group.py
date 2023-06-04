from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .commit import ConventionalCommit
    from .commit_type import CommitType


class CommitGroup:
    def __init__(
        self,
        commit_type: CommitType,
        title: str,
        commits: list[ConventionalCommit] = [],
    ) -> None:
        self.commit_type = commit_type
        self.title = title
        self.commits = commits or []
