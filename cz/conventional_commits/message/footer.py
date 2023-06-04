from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeAlias

if TYPE_CHECKING:
    from .message import Message

FooterPrefixType: TypeAlias = str
LinesType: TypeAlias = list[str]
AllFooterLinesType: TypeAlias = dict[FooterPrefixType, list[LinesType]]


class BaseFooter(ABC):
    PREFIX: FooterPrefixType
    MULTIPLE_MAX = 1
    LINES_MAX = 1

    @classmethod
    @abstractmethod
    def ask(cls, message: Message, question: Any) -> None:
        pass

    def __init__(self, message: Message, footer: AllFooterLinesType) -> None:
        self.validete_footer(message, footer)

    @abstractmethod
    def validete_footer(self, message: Message, footer: AllFooterLinesType) -> None:
        pass
