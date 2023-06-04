from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .message.message import Message
    from .tag import Tag
    from .user import User


class Hash:
    def __init__(self, long: str, short: str) -> None:
        self.long = long
        self.shor = short


class ConventionalCommit:
    def __init__(
        self,
        hash: Hash,
        author: User,
        committer: User,
        message: Message,
        tags: dict[str, Tag],
    ) -> None:
        self.hash = hash
        self.author = author
        self.committer = committer
        self.message = message
        self.tags = tags

        self.type = message.commit_type
        self.scope = message.scope
        self.is_breaking = message.is_breaking
