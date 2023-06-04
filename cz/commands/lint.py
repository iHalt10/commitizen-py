import re
from pathlib import Path
from typing import Optional

from cleo.io.inputs.option import Option

from .command import BaseCommand

# TODO
# cz lint --rev=<hash>
# cz lint --rev=<tag>
# cz lint --rev=<hash>..<hash>
# cz lint --rev=<tag>..<tag>


class LintCommand(BaseCommand):
    HASH_RANGE_REGEX = re.compile(r"(?P<start>[0-9a-f]{40})..(?P<end>[0-9a-f]{40})")
    name = "lint"
    description = ""
    options = [
        Option(
            name="rev",
            description="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            flag=False,
            requires_value=True,
        ),
        Option(
            name="commit-msg-file",
            description="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            flag=False,
            requires_value=True,
        ),
    ]

    def handle(self) -> int:
        rev: Optional[str] = self.option("rev")
        commit_msg_file: Optional[str] = self.option("commit-msg-file")

        if isinstance(rev, str) and isinstance(commit_msg_file, str):
            raise ValueError("Only one option can be selected.")

        if rev:
            result = self.HASH_RANGE_REGEX.fullmatch(rev)
            if result:
                self.api.lint_commits(
                    start=result.group("start"), end=result.group("end")
                )
            else:
                raise ValueError("not rev format")
        elif commit_msg_file:
            commit_msg_path = Path(commit_msg_file)
            self.api.lint_message(commit_msg_path.read_text())
        else:
            self.api.lint_commits()

        return 0
