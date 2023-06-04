from __future__ import annotations

import re
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import Type

from cz.conventional_commits.message.message import Message
from cz.exceptions import InvalidCommitMessageError

if TYPE_CHECKING:
    from cz.conventional_commits.commit_type import CommitType

    from .footer import AllFooterLinesType
    from .footer import BaseFooter
    from .footer import FooterPrefixType


class MessageParser:
    def __init__(
        self,
        commit_types: dict[str, CommitType],
        footer_classes: dict[FooterPrefixType, Type[BaseFooter]],
    ) -> None:
        self.COMMIT_TYPES = commit_types
        self.FIRST_LINE_REGEX = re.compile(
            r"(?P<type>"
            + "|".join(commit_types)
            + r")"
            + r"(?:\((?P<scope>\w+)\))?(?P<breaking>!)?: (?P<subject>.+)"
        )
        self.FOOTER_CLASSES = footer_classes

    def parse(self, msg: str) -> Message:
        msg = msg.rstrip()
        lines = msg.split("\n")
        first_line = self.parse_1st_line(lines)
        footer: dict[str, Any] = {}
        commit_type = self.COMMIT_TYPES[first_line["type"]]
        message = Message(
            commit_type=commit_type,
            scope=first_line["scope"],
            is_breaking=True if first_line["breaking"] else False,
            subject=first_line["subject"],
            body=None,
            footer=footer,
        )

        if len(lines) > 1:
            self.must_blank_line(lines, 1)
            body_lines, footer_types = self.parse_after_2nd_lines(lines[2:])

            message.body = "\n".join(body_lines)
            for prefix in footer_types:
                klass = self.FOOTER_CLASSES[prefix]
                message.footer[prefix] = klass(message=message, footer=footer_types)

        return message

    def parse_1st_line(self, lines: list[str]) -> dict[str, str]:
        result = self.FIRST_LINE_REGEX.fullmatch(lines[0])
        if not result:
            raise InvalidCommitMessageError(
                """Commit alidation: 1st line failed!
please enter a commit message in the conventional commits format.
Regex Pattern:
{0}
Success example:
- feat: add a
- feat(module_x): add b
- feat!: add c
- feat!: add d #12
Failure example:
- not_type: add a
- feat : add a
  - Don't include extra space
- feat:add a
  - Please open a space to the right of colon""".format(
                    self.FIRST_LINE_REGEX.pattern
                )
            )
        return result.groupdict()

    def parse_after_2nd_lines(
        self, lines: list[str]
    ) -> tuple[list[str], AllFooterLinesType]:
        body: list[str] = []
        footer: AllFooterLinesType = {}
        phase: Literal["BODY"] | Type[BaseFooter] = "BODY"
        footer_lines: list[str] = []
        footer_now_index = 0
        for line in lines:
            for i, klass in enumerate(self.FOOTER_CLASSES.values()):
                if line.startswith(f"{klass.PREFIX}:"):
                    if i < footer_now_index:
                        raise RuntimeError("順序が違います。")
                    if footer_lines and footer_lines[len(footer_lines) - 1] == "":
                        raise RuntimeError("改行いれないで")
                    footer_lines = []

                    target_footers = footer.setdefault(klass.PREFIX, [])
                    if (
                        klass.MULTIPLE_MAX > 0
                        and len(target_footers) >= klass.MULTIPLE_MAX
                    ):
                        raise RuntimeError("AA")
                    target_footers.append(footer_lines)

                    footer_now_index = i
                    phase = klass
                    break
            if phase == "BODY":
                body.append(line)
            else:
                if (
                    line != ""
                    and phase.LINES_MAX > 0
                    and len(footer_lines) >= phase.LINES_MAX
                ):
                    raise RuntimeError("BB")
                footer_lines.append(line)
        if body and body[len(body) - 1] != "":
            raise RuntimeError("body 改行を入れてね")
        if footer_lines and footer_lines[len(footer_lines) - 1] == "":
            raise RuntimeError("last 改行いれないで")
        return body, footer

    def must_blank_line(self, lines: list[str], pos: int) -> None:
        if (
            (pos != 0 and lines[pos - 1] == "")
            or lines[pos] != ""
            or (len(lines) - 1 > pos and lines[pos + 1] == "")
        ):
            raise InvalidCommitMessageError(
                """Be sure to insert "BLANK LINE" on the {0} line.
Commit Format:
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>""".format(
                    pos
                )
            )
