from cz.config import CommitizenConfig
from cz.defaults import BreakingChangeFooter
from cz.defaults import ClosesFooter
from cz.defaults import RevertHashFooter
from cz.versioning import VersionAttributes

config = CommitizenConfig()

config.set_repository_url("https://github.com/commitizen-tools/commitizen")

feat = config.create_comit_type("feat")
fix = config.create_comit_type("fix")
perf = config.create_comit_type("perf")
refactor = config.create_comit_type("refactor")
build = config.create_comit_type("build")
ci = config.create_comit_type("ci")
docs = config.create_comit_type("docs")
style = config.create_comit_type("style")
test = config.create_comit_type("test")
wip = config.create_comit_type("wip")
revert = config.create_comit_type("revert")
config.create_comit_type("bump")
config.create_comit_type("chore")

config.add_title(feat, "Features")
config.add_title(fix, "Bug Fixes")
config.add_title(perf, "Performance Improvements")
config.add_title(refactor, "Code Refactoring")
config.add_title(revert, "Revert")

config.add_increment(feat, VersionAttributes.MINOR)
config.add_increment(fix, VersionAttributes.PATCH)
config.add_increment(perf, VersionAttributes.PATCH)
config.add_increment(refactor, VersionAttributes.PATCH)

config.add_footer_class(BreakingChangeFooter)
config.add_footer_class(ClosesFooter)
config.add_footer_class(RevertHashFooter)

config.questions["en_US"] = {
    "Q1": {
        "subject": "Select Commit Type:",
        "choices": [
            {"commit_type": feat, "description": "A new feature"},
            {"commit_type": fix, "description": "A bug fix"},
            {"commit_type": docs, "description": "Documentation only changes"},
            {
                "commit_type": style,
                "description": "Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)",
            },
            {
                "commit_type": refactor,
                "description": "A code change that neither fixes a bug nor adds a feature",
            },
            {
                "commit_type": perf,
                "description": "A code change that improves performance",
            },
            {
                "commit_type": test,
                "description": "Adding missing tests or correcting existing tests",
            },
            {
                "commit_type": build,
                "description": "Changes that affect the build system or external dependencies",
            },
            {
                "commit_type": ci,
                "description": "Changes to our CI configuration files and scripts",
            },
            {"commit_type": wip, "description": "Work in progress"},
        ],
    },
    "Q2": {
        "subject": "What is the scope of this commit? (class or file name): (press [enter] to skip)"
    },
    "Q3": {"subject": "What is the subject of this commit?:"},
    "Q4": {"subject": "What is the body of this commit?:"},
    "Q5": {"subject": "Are there any breaking changes?:"},
    "footer": {
        BreakingChangeFooter.PREFIX: {
            "subject": "[Footer] Are there any breaking changes note?:"
        },
        ClosesFooter.PREFIX: {
            "subject": "[Footer] Issues Close Number: (press enter to skip)"
        },
    },
}

config.questions["ja_JP"] = {
    "Q1": {
        "subject": "Commit Type を選択:",
        "choices": [
            {"commit_type": feat, "description": "新機能"},
            {"commit_type": fix, "description": "バグ修正"},
            {"commit_type": docs, "description": "ドキュメントのみの変更"},
            {
                "commit_type": style,
                "description": "Cフォーマットの変更（コードの動作に影響しないスペース、フォーマット、セミコロンなど）",
            },
            {
                "commit_type": refactor,
                "description": "リファクタリングのための変更（機能追加やバグ修正を含まない）",
            },
            {
                "commit_type": perf,
                "description": "パフォーマンスの改善のための変更",
            },
            {
                "commit_type": test,
                "description": "不足テストの追加や既存テストの修正",
            },
            {
                "commit_type": build,
                "description": "ビルドシステムや外部依存に関する変更（スコープ例: gulp, broccoli, npm）",
            },
            {
                "commit_type": ci,
                "description": "CI用の設定やスクリプトに関する変更（スコープ例: Travis, Circle, BrowserStack, SauceLabs)",
            },
            {"commit_type": wip, "description": "進行中の作業"},
        ],
    },
    "Q2": {"subject": "Commit のスコープ:（enterでスキップ）"},
    "Q3": {"subject": "このコミットの要約は?:"},
    "Q4": {"subject": "このコミットの本文は?:"},
    "Q5": {"subject": "重大な変更はありますか?:"},
    "footer": {
        BreakingChangeFooter.PREFIX: {"subject": "[Footer] 重大な変更のノート?:"},
        ClosesFooter.PREFIX: {"subject": "[Footer] Issues クローズ番号?:（enterでスキップ）"},
    },
}
