from __future__ import annotations


class CommitType:
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
