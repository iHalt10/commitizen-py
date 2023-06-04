# pyright: reportUnknownMemberType=false
from pathlib import Path
from typing import Optional

import mdformat
from semver.version import Version

from cz.config import CommitizenConfig
from cz.conventional_commits.commit import ConventionalCommit
from cz.conventional_commits.message.parser import MessageParser
from cz.global_variables import GlobalVariables
from cz.versioning import VersionAttributes
from cz.versioning.files import VersionFiles

from .cc import ConventionalCommitsAPI
from .git import GitAPI


class CommitizenAPI:
    def __init__(
        self, config: CommitizenConfig, global_variables: Optional[GlobalVariables] = None
    ) -> None:
        self._config = config
        self.global_variables = global_variables or GlobalVariables()
        self.cc = ConventionalCommitsAPI(self._config, self.global_variables)
        self.git = GitAPI(config, self.global_variables)

    def bump_version(
        self, prerelease: Optional[str] = None, is_commit: bool = True
    ) -> tuple[Version, Optional[Version]]:
        version_files = VersionFiles(self._config.init_version_files_fn(self._config))
        current_version = version_files.get_version()
        next_version: Optional[Version] = None
        if prerelease:
            if (
                current_version.prerelease
                and prerelease
                != current_version.prerelease[: current_version.prerelease.find(".")]
            ):
                current_version = current_version.finalize_version()
            next_version = current_version.bump_prerelease(prerelease)
        elif current_version.prerelease:
            next_version = current_version.finalize_version()
        else:
            current_version_string = f"{current_version}"
            tags = self.cc.get_tags()
            if current_version_string == "0.0.0":
                commits = self.cc.get_commits(is_version=True)
                if self.global_variables.version_groups:
                    versions = [tag.name for tag in self.global_variables.version_groups]
                    raise RuntimeError(
                        f"""Unable to determine next version
        Commits from First Commit to HEAD are tagged with the version.
        Other Versions: {versions}"""
                    )
            else:
                if current_version_string not in tags:
                    raise RuntimeError(
                        f"The current version ({current_version}) is not tagged"
                    )
                commits = self.cc.get_commits(
                    start=current_version_string, is_version=True
                )
                if self.global_variables.version_groups:
                    versions = [tag.name for tag in self.global_variables.version_groups]
                    raise RuntimeError(
                        f"""Unable to determine next version
        Commits from {current_version} to "HEAD" have "version tagging" other than the current version.
        Current Version: {current_version}
        Other Version: {versions}"""
                    )

            next_version = self._increment_version(commits, current_version)

        if next_version:
            version_files.set_version(next_version)
            if is_commit:
                files: list[Path] = []
                for version_file in version_files.version_files:
                    if version_file.IS_COMMIT:
                        files.append(version_file.get_path())
                    pass
                if files:
                    self.git.add(files)
                    self.git.commit(f"bump: version {current_version} → {next_version}")
                    next_version_tag = self._config.format_tag_fn(next_version)
                    self.git.tag(next_version_tag)
            return current_version, next_version
        return current_version, next_version

    def _increment_version(
        self, commits: dict[str, ConventionalCommit], version: Version
    ) -> Optional[Version]:
        bump_map = self._config.bump_map
        increment: Optional[VersionAttributes] = None
        for commit in commits.values():
            if commit.is_breaking:
                increment = VersionAttributes.MAJOR
                break
            elif commit.type in bump_map:
                if increment != VersionAttributes.MINOR:
                    increment = bump_map[commit.type]
        if increment:
            return version.next_version(increment.value)
        return None

    def lint_commits(
        self,
        start: Optional[str] = None,
        end: str = "HEAD",
    ) -> None:
        self.cc.get_commits(start, end)

    def lint_message(self, msg: str) -> None:
        message_parser = MessageParser(
            self._config.commit_types, self._config.footer_classes
        )
        message_parser.parse(msg)

    def generate_changelog(self) -> str:
        self.cc.get_tags()
        self.cc.get_commits(is_version=True)
        changelog = self._config.changelog_template.render(
            version_groups=self.global_variables.version_groups,
            repository_url=self._config.repository_url,
        )
        return mdformat.text(changelog)
