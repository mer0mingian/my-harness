"""Resolver — expand skill glob patterns into explicit skill lists, then
emit per-phase ACLs in Claude Code and OpenCode formats.

Flow:
    scan_marketplace(root)            -> SkillCatalog
    expand_globs(patterns, catalog)   -> list[str]        # resolved skill names
    compile_phase_acl(phase, catalog) -> PhaseACL
    emit_claude_acl(acl)              -> dict
    emit_opencode_acl(acl)            -> dict[str, Literal["allow","deny"]]

Pattern grammar (union-then-subtract semantics):
    "stdd-pm-*"   glob match (fnmatch)
    "stdd-"       prefix match — normalized to "stdd-*"
    "stdd-tdd"    exact match
    ""            match-all — normalized to "*"
    "!stdd-tdd"   negation: remove matches from the accumulated include set
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Iterable

import frontmatter

from .schemas import PhaseManifest, Skill


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SkillCatalog:
    """Scanned marketplace snapshot: skill name -> Skill metadata."""

    skills: dict[str, Skill] = field(default_factory=dict)

    def names(self) -> list[str]:
        return sorted(self.skills.keys())


@dataclass
class PhaseACL:
    """Resolved per-phase access-control data, pre-emission."""

    phase_name: str
    allowed_skills: list[str]
    allowed_tools: list[str] | None = None
    bash_scope: str | None = None
    external_apis: list[str] = field(default_factory=list)
    write_access: str | bool = True


# ---------------------------------------------------------------------------
# Pattern normalization + glob expansion
# ---------------------------------------------------------------------------


def _normalize_pattern(pattern: str) -> str:
    """Normalize a single pattern into an fnmatch-compatible glob."""
    if not pattern:
        return "*"
    if pattern.endswith("-") and "*" not in pattern:
        return pattern + "*"
    return pattern


def expand_globs(patterns: Iterable[str], catalog: SkillCatalog) -> list[str]:
    """Resolve a list of patterns into a sorted list of matching skill names."""
    includes: list[str] = []
    excludes: list[str] = []
    for p in patterns:
        if p.startswith("!"):
            excludes.append(_normalize_pattern(p[1:]))
        else:
            includes.append(_normalize_pattern(p))

    all_names = catalog.names()
    included: set[str] = set()
    for glob in includes:
        included.update(n for n in all_names if fnmatchcase(n, glob))
    for glob in excludes:
        included = {n for n in included if not fnmatchcase(n, glob)}
    return sorted(included)


# ---------------------------------------------------------------------------
# Marketplace scan
# ---------------------------------------------------------------------------


def scan_marketplace(root: Path) -> SkillCatalog:
    """Walk the tree under `root`, parse SKILL.md files, and build the catalog.

    Skills whose SKILL.md is missing frontmatter or whose frontmatter fails
    schema validation are silently skipped — the validator CLI is the
    authoritative tool for reporting such issues. The resolver's job is to
    produce a usable catalog from whatever validates cleanly.
    """
    catalog = SkillCatalog()
    for p in root.rglob("SKILL.md"):
        if p.parent == root:
            continue
        try:
            post = frontmatter.load(p)
        except Exception:
            continue
        if not post.metadata:
            continue
        try:
            skill = Skill.model_validate(dict(post.metadata))
        except Exception:
            continue
        catalog.skills[skill.name] = skill
    return catalog


# ---------------------------------------------------------------------------
# Phase-ACL compilation
# ---------------------------------------------------------------------------


def compile_phase_acl(phase: PhaseManifest, catalog: SkillCatalog) -> PhaseACL:
    """Resolve a phase manifest's skill globs + constraints into a PhaseACL."""
    allowed_skills = expand_globs(phase.skills, catalog)
    bash_scope: str | None = None
    external_apis: list[str] = []
    write_access: str | bool = True
    if phase.constraints:
        bash_scope = phase.constraints.bash_scope
        external_apis = list(phase.constraints.external_apis)
        write_access = phase.constraints.write_access
    return PhaseACL(
        phase_name=phase.name,
        allowed_skills=allowed_skills,
        allowed_tools=None,
        bash_scope=bash_scope,
        external_apis=external_apis,
        write_access=write_access,
    )


# ---------------------------------------------------------------------------
# CLI-specific emitters
# ---------------------------------------------------------------------------


def emit_claude_acl(acl: PhaseACL) -> dict:
    """Claude Code-shaped dict for a phase.

    Claude Code's tool allowlist (`allowed-tools`) is orthogonal to skills;
    skills are prompt-level capability advertisements. We return both so
    downstream hook code can decide how to use each.
    """
    return {
        "phase": acl.phase_name,
        "allowed_skills": list(acl.allowed_skills),
        "allowed_tools": list(acl.allowed_tools or []),
        "bash_scope": acl.bash_scope,
        "external_apis": list(acl.external_apis),
        "write_access": acl.write_access,
    }


def emit_opencode_acl(acl: PhaseACL) -> dict[str, str]:
    """OpenCode-style permission.skill dict: literal allows + wildcard deny."""
    out: dict[str, str] = {name: "allow" for name in acl.allowed_skills}
    out[""] = "deny"  # OpenCode convention: empty-key default
    return out


__all__ = [
    "PhaseACL",
    "SkillCatalog",
    "compile_phase_acl",
    "emit_claude_acl",
    "emit_opencode_acl",
    "expand_globs",
    "scan_marketplace",
]
