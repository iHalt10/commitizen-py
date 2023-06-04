from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Tag:
    type = "lightweight"

    def __init__(self, name: str, commit_id: str, creator: User) -> None:
        self.commit_id = commit_id
        self.name = name
        self.creator = creator

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"


class AnnotatedTag(Tag):
    type = "annotated"
