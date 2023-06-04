from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import TypedDict

if TYPE_CHECKING:
    from .conventional_commits.commit_type import CommitType


class ChoicePatternA(TypedDict):
    commit_type: CommitType
    description: str


class QuestionPatternA(TypedDict):
    subject: str
    choices: list[ChoicePatternA]


class QuestionPatternB(TypedDict):
    subject: str


class Question(TypedDict):
    Q1: QuestionPatternA
    Q2: QuestionPatternB
    Q3: QuestionPatternB
    Q4: QuestionPatternB
    Q5: QuestionPatternB
    footer: dict[str, Any]
