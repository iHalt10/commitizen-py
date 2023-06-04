from typing import Optional

from cleo.io.inputs.option import Option

from .command import BaseCommand


class BumpCommand(BaseCommand):
    name = "bump"
    description = ""
    options = [
        Option(
            name="prerelease",
            description="prerelease",
            shortcut="p",
            flag=False,
            requires_value=True,
        ),
        Option(
            name="no-commit",
            description="no commit",
        ),
    ]

    def handle(self) -> int:
        is_commit = not bool(self.option("no-commit"))
        prerelease: Optional[str] = self.option("prerelease")
        current_version, next_version = self.api.bump_version(prerelease, is_commit)
        self.line(f"Current: {current_version}")
        self.line(f"Next: {next_version}")
        return 0
