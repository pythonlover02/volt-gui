import subprocess
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import Final


EXT_ID: Final[str] = "org.freedesktop.Platform.VulkanLayer.volt"
PLATFORM_ID: Final[str] = "org.freedesktop.Platform"
SDK_ID: Final[str] = "org.freedesktop.Sdk"
ARCH: Final[str] = "x86_64"
BRANCH_TEMPLATE: Final[str] = "runtime/{ext}/{arch}/{rt}"
SUBJECT_PREFIX: Final[str] = "volt extension "
OSTREE_BIN: Final[str] = "ostree"

METADATA_TEMPLATE: Final[str] = """\
[Runtime]
name={ext}
runtime={platform}/{arch}/{rt}
sdk={sdk}/{arch}/{rt}

[ExtensionOf]
ref=runtime/{platform}/{arch}/{rt}
"""


@dataclass(frozen=True)
class CommitArgs:
    rt: str
    repo: Path
    stage: Path


@dataclass(frozen=True)
class CommitPlan:
    branch: str
    subject: str
    metadata: str
    stage_metadata_path: Path
    repo: Path
    stage: Path


def parse_argv(argv: list[str]) -> CommitArgs:
    _, rt, repo, stage = argv
    return CommitArgs(rt=rt, repo=Path(repo), stage=Path(stage))


def render_metadata(rt: str) -> str:
    return METADATA_TEMPLATE.format(
        ext=EXT_ID, platform=PLATFORM_ID, sdk=SDK_ID, arch=ARCH, rt=rt
    )


def build_plan(args: CommitArgs) -> CommitPlan:
    return CommitPlan(
        branch=BRANCH_TEMPLATE.format(ext=EXT_ID, arch=ARCH, rt=args.rt),
        subject=SUBJECT_PREFIX + args.rt,
        metadata=render_metadata(args.rt),
        stage_metadata_path=args.stage / "metadata",
        repo=args.repo,
        stage=args.stage,
    )


def build_command(plan: CommitPlan) -> list[str]:
    return [
        OSTREE_BIN,
        "commit",
        f"--repo={plan.repo}",
        f"--branch={plan.branch}",
        f"--subject={plan.subject}",
        f"--add-metadata-string=xa.metadata={plan.metadata}",
        str(plan.stage),
    ]


def call_write_text(path: Path, content: str) -> None:
    path.write_text(content)


def call_run(cmd: list[str]) -> int:
    return subprocess.run(cmd).returncode


def main() -> int:
    plan = build_plan(parse_argv(sys.argv))
    call_write_text(plan.stage_metadata_path, plan.metadata)
    return call_run(build_command(plan))


sys.exit(main())
