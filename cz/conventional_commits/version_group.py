from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional

if TYPE_CHECKING:
    from .commit_group import CommitGroup
    from .tag import Tag


class VersionGroup:
    def __init__(
        self, tag: Tag, commit_groups: dict[str, CommitGroup] = {}, notes: list[str] = []
    ) -> None:
        self.tag = tag
        self.commit_groups = commit_groups or {}
        self.notes: list[str] = notes or []
        self.next: Optional[VersionGroup] = None
        self.previous: Optional[VersionGroup] = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.tag.name}>"
