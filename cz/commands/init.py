from pathlib import Path
from typing import Optional

import questionary
from cleo.commands.command import Command
from cleo.io.inputs.option import Option


class InitCommand(Command):
    name = "init"
    description = "XXXXX"
    options = [
        Option(
            name="repository_url",
            description="Github Repository URL",
            shortcut="url",
            flag=False,
            requires_value=True,
        )
    ]

    def handle(self) -> int:
        repository_url: Optional[str] = self.option("repository_url")
        if repository_url is None:
            repository_url = str(questionary.text("Github Repository URL?").ask())

        from cz.templates import config as config_module

        config_module_path = Path(config_module.__file__)
        changelog_template_path = Path(f"{config_module_path.parents[0]}/CHANGELOG.j2")

        config_module_string = config_module_path.read_text()
        config_module_string = config_module_string.replace(
            config_module.config.repository_url, repository_url
        )
        changelog_template_string = changelog_template_path.read_text()

        user_conifg_path = Path(".cz")
        user_conifg_path.mkdir(exist_ok=True)
        Path(f"{user_conifg_path}/config.py").write_text(config_module_string)
        Path(f"{user_conifg_path}/CHANGELOG.j2").write_text(changelog_template_string)
        return 0
