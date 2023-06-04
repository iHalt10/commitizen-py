from __future__ import annotations

import locale
import re
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

import questionary
from cleo.io.inputs.option import Option
from questionary import Choice

# from cz.defaults import BreakingChangeFooter
# from cz.defaults import ClosesFooter
from cz.conventional_commits.message.message import Message

from .command import BaseCommand

if TYPE_CHECKING:
    from cz.conventional_commits.commit_type import CommitType


class CommitCommand(BaseCommand):
    name = "commit"
    description = ""
    options = [
        Option(
            name="signoff",
            description="TODO",
            shortcut="s",
        )
    ]
    aliases = ["c"]

    def handle(self) -> int:
        language, _ = locale.getlocale()
        if not language:
            raise RuntimeError()
        if "en_US" not in self.config.questions:
            raise RuntimeError("No default en_US language is set in the config file")
        if language in self.config.questions:
            question = self.config.questions[language]
        else:
            question = self.config.questions["en_US"]
        choices: list[Choice] = []
        for choice_data in question["Q1"]["choices"]:
            choices.append(
                Choice(
                    title=f"{choice_data['commit_type'].name}: {choice_data['description']}",
                    value=choice_data["commit_type"],
                )
            )
        commit_type: CommitType = questionary.select(
            question["Q1"]["subject"],
            choices=choices,
        ).ask()
        scope: Optional[str] = questionary.text(question["Q2"]["subject"]).ask()
        subject: str = questionary.text(question["Q3"]["subject"]).ask()
        body: Optional[str] = questionary.text(
            question["Q4"]["subject"], multiline=True
        ).ask()
        is_breaking = questionary.confirm(question["Q5"]["subject"], default=False).ask()
        if scope == "":
            scope = None
        if body == "":
            body = None
        elif isinstance(body, str):
            body = re.sub(r"\n\n+", "\n", body)
            body = body.rstrip()

        footer: dict[str, Any] = {}
        message = Message(commit_type, scope, is_breaking, subject, body, footer)
        for footer_class in self.config.footer_classes.values():
            if footer_class.PREFIX in question["footer"]:
                footer_class.ask(message, question["footer"][footer_class.PREFIX])

        # self.api.git.commit(message.to_string())

        return 0
