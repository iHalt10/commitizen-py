import subprocess
from pathlib import Path
from typing import Optional

from cz.config import CommitizenConfig
from cz.global_variables import GlobalVariables


class GitAPI:
    def __init__(
        self, config: CommitizenConfig, global_variables: Optional[GlobalVariables] = None
    ) -> None:
        self._config = config
        self.global_variables = global_variables or GlobalVariables()

    def add(self, paths: list[Path]) -> None:
        git_add_cmd = ["git", "add"] + [f"{path}" for path in paths]
        subprocess.run(
            git_add_cmd, capture_output=True, check=True, cwd=self._config.repository_path
        )

    def commit(self, msg: str) -> None:
        git_commit_cmd = ["git", "commit"]
        lines = msg.split("\n")
        for line in lines:
            git_commit_cmd.append("-m")
            git_commit_cmd.append(line)
        subprocess.run(
            git_commit_cmd,
            capture_output=True,
            check=True,
            cwd=self._config.repository_path,
        )

    def tag(self, name: str) -> None:
        git_tag_cmd = ["git", "tag", name]
        subprocess.run(
            git_tag_cmd, capture_output=True, check=True, cwd=self._config.repository_path
        )
