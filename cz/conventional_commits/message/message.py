from __future__ import annotations

import re
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

if TYPE_CHECKING:
    from cz.conventional_commits.commit_type import CommitType


class Message:
    def __init__(
        self,
        commit_type: CommitType,
        scope: Optional[str],
        is_breaking: bool,
        subject: str,
        body: Optional[str],
        footer: dict[str, Any],
    ):
        self.commit_type = commit_type
        self.scope = scope
        self.is_breaking = is_breaking
        self.subject = subject
        self.body = body
        self.footer = footer

    def subject_to_markdown(self, url: str) -> str:
        subject = self.subject
        closes: list[str] = re.findall(r"#\d+", subject)
        for close in closes:
            close_id = close[1:]
            subject = subject.replace(close, f"[{close}]({url}/pull/{close_id})", 1)
        return subject

    def to_string(self) -> str:
        msg = self.commit_type.name
        if self.scope:
            msg = f"{msg}({msg})"
        if self.is_breaking:
            msg = f"{msg}!"
        msg = f"{msg}: {self.subject}"
        if self.body:
            msg = f"{msg}\n\n{self.body}"

        if self.footer:
            footer = ""
            for footer_prefix in self.footer:
                footer = f"{footer}{self.footer[footer_prefix]}\n"
            footer = footer.rstrip()
            msg = f"{msg}\n\n{footer}"
        return msg
