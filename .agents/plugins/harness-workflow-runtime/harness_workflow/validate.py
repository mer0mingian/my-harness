"""Validator CLI for the harness-workflow-runtime schemas.

Usage:
    python -m harness_workflow.validate PATH [PATH ...]
    python -m harness_workflow.validate --strict PATH
    python -m harness_workflow.validate --json PATH

Discovers and validates:
    * SKILL.md        (skills/<name>/SKILL.md)
    * Agent .md       (agents/*.md)
    * Command .md     (commands/*.md)
    * workflow.yaml   (workflow manifests, recursively)

Exit codes:
    0  clean (no issues, or warnings-only without --strict)
    1  warnings encountered with --strict
    2  validation errors encountered
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import frontmatter
import yaml
from pydantic import ValidationError

from .schemas import Agent, Command, Skill, WorkflowManifest


# ---------------------------------------------------------------------------
# Issue type
# ---------------------------------------------------------------------------


@dataclass
class Issue:
    level: str  # "error" | "warning"
    path: str
    message: str

    def format(self) -> str:
        tag = "ERROR" if self.level == "error" else "WARN "
        return f"{tag}  {self.path}: {self.message}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fmt_validation_error(e: ValidationError) -> str:
    parts = []
    for err in e.errors():
        loc = ".".join(str(x) for x in err["loc"]) or "<root>"
        parts.append(f"{loc}: {err['msg']}")
    return "; ".join(parts)


def _load_frontmatter(path: Path) -> tuple[dict | None, str, str | None]:
    """Return (metadata, body, error_message)."""
    try:
        post = frontmatter.load(path)
    except Exception as e:  # broad: YAML parse errors, encoding, etc.
        return None, "", f"failed to parse frontmatter: {e}"
    if not post.metadata:
        return None, post.content or "", "file has no YAML frontmatter"
    return dict(post.metadata), post.content or "", None


# ---------------------------------------------------------------------------
# Per-artifact validators
# ---------------------------------------------------------------------------


def validate_skill(path: Path) -> list[Issue]:
    issues: list[Issue] = []
    meta, body, err = _load_frontmatter(path)
    if err:
        return [Issue("error", str(path), err)]

    try:
        skill = Skill.model_validate(meta)
    except ValidationError as e:
        return [Issue("error", str(path), _fmt_validation_error(e))]

    # Body length (warn)
    body_lines = len(body.splitlines())
    if body_lines > 500:
        issues.append(
            Issue(
                "warning",
                str(path),
                f"SKILL.md body has {body_lines} lines (agentskills.io recommends <=500)",
            )
        )

    # Directory name vs frontmatter name (warn only — 19 mismatches exist today;
    # the deferred skill-naming audit will decide whether to enforce later).
    dir_name = path.parent.name
    if dir_name != skill.name:
        issues.append(
            Issue(
                "warning",
                str(path),
                f"directory name {dir_name!r} differs from skill name {skill.name!r}",
            )
        )
    return issues


def validate_agent(path: Path) -> list[Issue]:
    meta, _body, err = _load_frontmatter(path)
    if err:
        return [Issue("error", str(path), err)]
    try:
        Agent.model_validate(meta)
    except ValidationError as e:
        return [Issue("error", str(path), _fmt_validation_error(e))]
    return []


def validate_command(path: Path) -> list[Issue]:
    meta, _body, err = _load_frontmatter(path)
    # Commands may legitimately have no frontmatter — treat as no-op.
    if err == "file has no YAML frontmatter":
        return []
    if err:
        return [Issue("error", str(path), err)]
    try:
        Command.model_validate(meta)
    except ValidationError as e:
        return [Issue("error", str(path), _fmt_validation_error(e))]
    return []


def validate_workflow(path: Path) -> list[Issue]:
    try:
        with path.open() as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [Issue("error", str(path), f"failed to parse YAML: {e}")]
    if data is None:
        return [Issue("error", str(path), "workflow.yaml is empty")]
    try:
        WorkflowManifest.model_validate(data)
    except ValidationError as e:
        return [Issue("error", str(path), _fmt_validation_error(e))]
    return []


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def discover_skill_files(root: Path) -> list[Path]:
    """All SKILL.md files under `root` that live in a subdirectory."""
    out: list[Path] = []
    for p in root.rglob("SKILL.md"):
        # Defensive: skip SKILL.md sitting directly at the given root.
        if p.parent == root:
            continue
        out.append(p)
    return sorted(out)


def discover_workflow_files(root: Path) -> list[Path]:
    return sorted(root.rglob("workflow.yaml"))


def _collect(root: Path) -> dict[str, list[Path]]:
    """Dispatch a root path to the relevant file lists."""
    buckets: dict[str, list[Path]] = {
        "skill": [],
        "agent": [],
        "command": [],
        "workflow": [],
    }

    # SKILL.md + workflow.yaml found recursively everywhere.
    buckets["skill"] = discover_skill_files(root)
    buckets["workflow"] = discover_workflow_files(root)

    # Agents + commands: use layout heuristics.
    if root.name == "agents":
        buckets["agent"] = sorted(p for p in root.glob("*.md") if p.is_file())
    if root.name == "commands":
        buckets["command"] = sorted(p for p in root.glob("*.md") if p.is_file())

    for candidate in (root / ".agents" / "agents", root / "agents"):
        if candidate.is_dir() and candidate != root:
            buckets["agent"] += sorted(p for p in candidate.glob("*.md") if p.is_file())
    for candidate in (root / ".agents" / "commands", root / "commands"):
        if candidate.is_dir() and candidate != root:
            buckets["command"] += sorted(p for p in candidate.glob("*.md") if p.is_file())

    # Dedupe while preserving order.
    for k, v in buckets.items():
        buckets[k] = list(dict.fromkeys(v))
    return buckets


def _validate_single_file(path: Path) -> list[Issue]:
    if path.name == "SKILL.md":
        return validate_skill(path)
    if path.name == "workflow.yaml":
        return validate_workflow(path)
    if path.suffix == ".md":
        # Fallback: try the Agent model first, then Command if that fails hard.
        # In practice callers should pass a bucketed directory.
        meta, _body, err = _load_frontmatter(path)
        if err == "file has no YAML frontmatter":
            return []
        if err:
            return [Issue("error", str(path), err)]
        # Try Agent first
        try:
            Agent.model_validate(meta)
            return []
        except ValidationError:
            try:
                Command.model_validate(meta)
                return []
            except ValidationError as e:
                return [
                    Issue(
                        "error",
                        str(path),
                        f"does not validate as Agent or Command: {_fmt_validation_error(e)}",
                    )
                ]
    return []


# ---------------------------------------------------------------------------
# Runner + CLI
# ---------------------------------------------------------------------------


def run(paths: Iterable[Path]) -> list[Issue]:
    out: list[Issue] = []
    for raw in paths:
        p = Path(raw).resolve()
        if not p.exists():
            out.append(Issue("error", str(p), "path does not exist"))
            continue
        if p.is_file():
            out.extend(_validate_single_file(p))
            continue
        buckets = _collect(p)
        for sp in buckets["skill"]:
            out.extend(validate_skill(sp))
        for ap in buckets["agent"]:
            out.extend(validate_agent(ap))
        for cp in buckets["command"]:
            out.extend(validate_command(cp))
        for wp in buckets["workflow"]:
            out.extend(validate_workflow(wp))
    return out


def summary(issues: list[Issue]) -> str:
    errs = sum(1 for i in issues if i.level == "error")
    warns = sum(1 for i in issues if i.level == "warning")
    if not issues:
        return "OK — no issues."
    return f"{errs} error(s), {warns} warning(s)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="harness-workflow-validate",
        description="Validate harness-workflow marketplace artifacts.",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="files or directories to validate")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="emit JSON report instead of text")
    args = parser.parse_args(argv)

    issues = run(args.paths)
    has_errors = any(i.level == "error" for i in issues)
    has_warnings = any(i.level == "warning" for i in issues)

    if args.json:
        payload = {
            "summary": summary(issues),
            "has_errors": has_errors,
            "has_warnings": has_warnings,
            "issues": [asdict(i) for i in issues],
        }
        print(json.dumps(payload, indent=2))
    else:
        for i in issues:
            out_stream = sys.stderr if i.level == "error" else sys.stdout
            print(i.format(), file=out_stream)
        print(f"\n{summary(issues)}", file=sys.stderr)

    if has_errors:
        return 2
    if has_warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
