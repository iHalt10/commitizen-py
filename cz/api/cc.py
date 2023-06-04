from __future__ import annotations

import re
import subprocess
from typing import TYPE_CHECKING
from typing import Optional

from semver.version import Version

from cz.config import CommitizenConfig
from cz.conventional_commits.commit import ConventionalCommit
from cz.conventional_commits.commit import Hash
from cz.conventional_commits.commit_group import CommitGroup
from cz.conventional_commits.message.parser import MessageParser
from cz.conventional_commits.tag import AnnotatedTag
from cz.conventional_commits.tag import Tag
from cz.conventional_commits.user import User
from cz.conventional_commits.version_group import VersionGroup
from cz.exceptions import InvalidVersionError
from cz.global_variables import GlobalVariables

if TYPE_CHECKING:
    from cz.defaults import BreakingChangeFooter


class ConventionalCommitsAPI:
    def __init__(
        self, config: CommitizenConfig, global_variables: Optional[GlobalVariables] = None
    ) -> None:
        self.global_variables = global_variables or GlobalVariables()
        self._config = config

    def get_commits(
        self,
        start: Optional[str] = None,
        end: str = "HEAD",
        is_version: bool = False,
    ) -> dict[str, ConventionalCommit]:
        message_parser = MessageParser(
            self._config.commit_types, self._config.footer_classes
        )
        self.global_variables.commits = {}
        separator = "@@__CZ__@@"
        delimiter = "@@__CZ_DELIMITER__@@"
        fotmat = [
            # hash
            "%H",  # commit hash
            "%h",  # abbreviated commit hash
            # author
            "%an",  # author name
            "%ae",  # author email
            "%at",  # author date, UNIX timestamp
            # committer
            "%cn",  # committer name
            "%ce",  # committer email
            "%ct",  # committer date, UNIX timestamp
            # subject and body
            "%B",  # raw body (unwrapped subject and body)
            # refs (only tag)
            "%D",
        ]
        revision_range = f"{start}..{end}" if start else end
        git_log_cmd = [
            "git",
            "--no-pager",
            "log",
            "--decorate=short",
            "--decorate-refs=tags",
            f"--pretty={delimiter.join(fotmat)}{separator}",
            revision_range,
        ]
        completed_cmd = subprocess.run(
            git_log_cmd, capture_output=True, check=True, cwd=self._config.repository_path
        )
        commit_strings = completed_cmd.stdout.decode("utf-8").split(f"{separator}\n")
        commit_strings.pop()
        now_version: Optional[VersionGroup] = None
        for commit_string in commit_strings:
            commit_infos = commit_string.split(delimiter)
            commit_hash = Hash(commit_infos[0], commit_infos[1])
            author = User(
                name=commit_infos[2],
                email=commit_infos[3],
                unix_time=int(commit_infos[4]),
            )
            committer = User(
                name=commit_infos[5],
                email=commit_infos[6],
                unix_time=int(commit_infos[7]),
            )
            message = message_parser.parse(commit_infos[8])

            commit_tags = self._parse_tags(commit_infos[9])
            commit = ConventionalCommit(
                commit_hash, author, committer, message, commit_tags
            )
            self.global_variables.commits[commit_hash.long] = commit
            if is_version:
                version_tag: Optional[Tag] = self._get_only_one_version(commit_tags)
                if version_tag:
                    commit_groups: dict[str, CommitGroup] = {}
                    for commit_type, title in self._config.titles.items():
                        commit_groups[commit_type.name] = CommitGroup(commit_type, title)

                    now_version = self.global_variables.version_groups.setdefault(
                        version_tag, VersionGroup(version_tag, commit_groups)
                    )
                if now_version:
                    commit_group = now_version.commit_groups.get(message.commit_type.name)
                    if commit_group:
                        commit_group.commits.append(commit)
                        footer: Optional[BreakingChangeFooter] = message.footer.get(
                            "BREAKING CHANGE"
                        )
                        if footer:
                            now_version.notes.append(footer.body)
        if is_version:
            version_groups_list = list(self.global_variables.version_groups.values())
            for i, version_group in enumerate(version_groups_list):
                if i != 0:
                    version_group.next = version_groups_list[i - 1]
                if i != len(version_groups_list) - 1:
                    version_group.previous = version_groups_list[i + 1]
                for (
                    commit_type_name,
                    commit_group,
                ) in version_group.commit_groups.copy().items():
                    if not commit_group.commits:
                        del version_group.commit_groups[commit_type_name]
        return self.global_variables.commits.copy()

    def _get_only_one_version(self, tags: dict[str, Tag]) -> Optional[Tag]:
        version_tags: list[Tag] = []
        for tag in tags.values():
            if Version.isvalid(tag.name):
                version_tags.append(tag)

        if len(version_tags) == 0:
            return None
        if len(version_tags) == 1:
            return version_tags[0]
        raise InvalidVersionError("A commit cannot contain multiple version tags.")

    def _parse_tags(self, tags_line: str) -> dict[str, Tag]:
        result: dict[str, Tag] = {}
        if tags_line != "":
            for tag_string in tags_line.split(","):
                name = tag_string.strip("tag: ")
                result[name] = self.global_variables.tags[name]
        return result

    def get_tags(self) -> dict[str, Tag]:
        self.global_variables.tags = {}
        CREATOR_REGEX = re.compile(
            r"(?P<creator_name>.+) <(?P<creator_email>.+)> (?P<unix_time>\d+) (?P<timezone>.+)"
        )
        separator = "\n"
        delimiter = "\t"
        fotmat = ["%(objecttype)", "%(objectname)", "%(refname:short)", "%(creator)"]
        git_for_each_ref_cmd = [
            "git",
            "for-each-ref",
            "--sort=-creatordate",
            f"--format={delimiter.join(fotmat)}",
            "refs/tags",
        ]
        completed_cmd = subprocess.run(
            git_for_each_ref_cmd,
            capture_output=True,
            check=True,
            cwd=self._config.repository_path,
        )
        tag_strings = completed_cmd.stdout.decode("utf-8").split(separator)
        tag_strings.pop()
        for tag_string in tag_strings:
            object_type, commit_id, name, creator_string = tag_string.split(delimiter)
            result = CREATOR_REGEX.match(creator_string)
            if not result:
                raise RuntimeError(
                    "Normally this error does not occur. This is because of the type hint."
                )
            creator_name, creator_email, unix_time, _ = result.groups()
            creator = User(creator_name, creator_email, int(unix_time))
            tag_class = AnnotatedTag if object_type == "tag" else Tag
            self.global_variables.tags[name] = tag_class(name, commit_id, creator)
        return self.global_variables.tags.copy()
