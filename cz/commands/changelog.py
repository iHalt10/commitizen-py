from pathlib import Path
from typing import Optional

from cleo.io.inputs.option import Option

from .command import BaseCommand


class ChangeLogCommand(BaseCommand):
    name = "changelog"
    description = ""
    options = [
        Option(
            name="incremental",
            description="TODO",
        ),
        Option(
            name="stdout",
            description="Print CHANGELOG",
        ),
        Option(
            name="file-name",
            description="Output file",
            flag=False,
            requires_value=True,
        ),
        Option(
            name="unreleased-version",
            description="TODO",
            flag=False,
            requires_value=True,
        ),
        Option(
            name="start-rev",
            description="TODO",
            flag=False,
            requires_value=True,
        ),
    ]
    aliases = ["ch"]

    def handle(self) -> int:
        changelog = self.api.generate_changelog()
        stdout: bool = self.option("stdout")
        file_name: Optional[str] = self.option("file-name")
        file_path: Optional[Path] = None
        if file_name:
            file_path = Path(file_name)
        if stdout:
            self.line(changelog)
        if file_path:
            file_path.write_text(changelog)
        return 0
