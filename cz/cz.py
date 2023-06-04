from cleo.application import Application
from cleo.io.inputs.option import Option

from .__version__ import __version__
from .commands.bump import BumpCommand
from .commands.changelog import ChangeLogCommand
from .commands.commit import CommitCommand
from .commands.init import InitCommand
from .commands.lint import LintCommand

APP_NAME = "cz"


class CommitizenCLI(Application):
    def __init__(self) -> None:
        super().__init__(APP_NAME, __version__)
        self.definition.add_option(
            Option(
                name="repository_path",
                description="git repository directory",
                shortcut="r",
                flag=False,
                requires_value=True,
            )
        )
        self.add(BumpCommand())
        self.add(ChangeLogCommand())
        self.add(CommitCommand())
        self.add(InitCommand())
        self.add(LintCommand())
