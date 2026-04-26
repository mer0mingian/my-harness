"""Pydantic models for the harness workflow runtime.

Validation schemas for:
  * Skill           - SKILL.md frontmatter (agentskills.io spec)
  * Agent           - Agent markdown frontmatter (dual permission convention)
  * Permissions     - `permission.*` block, accepts OpenCode + STDD styles
  * Command         - Slash-command frontmatter (Claude native + STDD styles)
  * HookMatcher     - settings.json hook entries
  * PhaseManifest   - Single phase within a workflow
  * WorkflowManifest - Root workflow definition

One schema layer, three usages (see docs/WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md §5a):
  1. CI / pre-commit validation (validate.py)
  2. Install-time resolver (Phase 2; emits CLI-native ACLs)
  3. Runtime hooks (Phase 4; allow/deny decisions)
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

PermissionValue = Literal["allow", "deny", "ask"]

SkillName = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-z0-9][a-z0-9-]*$",
        min_length=1,
        max_length=64,
    ),
]

SemVer = Annotated[
    str,
    StringConstraints(pattern=r"^\d+\.\d+(\.\d+)?(-[a-zA-Z0-9.-]+)?$"),
]


# ---------------------------------------------------------------------------
# Skill (SKILL.md) — agentskills.io compliant
# ---------------------------------------------------------------------------


class Skill(BaseModel):
    """SKILL.md frontmatter per agentskills.io.

    Body length (recommended <=500 lines) is checked by the loader, not the model.
    """

    model_config = ConfigDict(extra="allow")

    name: SkillName
    description: Annotated[str, StringConstraints(min_length=1, max_length=1024)]
    compatibility: str | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("name")
    @classmethod
    def no_reserved_terms(cls, v: str) -> str:
        lowered = v.lower()
        if "claude" in lowered or "anthropic" in lowered:
            raise ValueError("skill name must not contain 'claude' or 'anthropic'")
        return v


# ---------------------------------------------------------------------------
# Permissions — accepts OpenCode + STDD conventions in one permissive model
# ---------------------------------------------------------------------------


class Permissions(BaseModel):
    """Permission ACL block on an agent.

    Two conventions coexist in the current marketplace:
      * OpenCode-style:  `permission.skill: {<glob>: allow|deny}`
      * STDD-style:      `permission.{read,write,edit,bash}: {<glob>: allow|deny}`

    Both are accepted. All fields optional; extra keys permitted for
    forward compatibility with OpenCode additions.
    """

    model_config = ConfigDict(extra="allow")

    # OpenCode-style
    skill: dict[str, PermissionValue] | None = None
    webfetch: dict[str, PermissionValue] | None = None

    # STDD-style
    read: dict[str, PermissionValue] | None = None
    write: dict[str, PermissionValue] | None = None
    edit: dict[str, PermissionValue] | None = None

    # Shared (appears in both conventions)
    bash: dict[str, PermissionValue] | None = None

    @property
    def style(self) -> Literal["opencode", "stdd", "unknown"]:
        if self.skill is not None:
            return "opencode"
        if any(f is not None for f in (self.read, self.write, self.edit)):
            return "stdd"
        return "unknown"


# ---------------------------------------------------------------------------
# Agent (AGENT.md)
# ---------------------------------------------------------------------------


class Agent(BaseModel):
    """Agent markdown-file frontmatter."""

    model_config = ConfigDict(extra="allow")

    name: str | None = None  # often matches filename; not required by the schema
    description: str
    model: str | None = None
    mode: Literal["subagent", "primary", "all"] | None = None
    source: str | None = None
    skills: list[str] = Field(default_factory=list)  # glob patterns
    tools: list[str] | None = None
    permission: Permissions | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)


# ---------------------------------------------------------------------------
# Command (slash-command frontmatter)
# ---------------------------------------------------------------------------


class Command(BaseModel):
    """Slash-command frontmatter — covers both Claude Code native and STDD formats."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    description: str

    # Claude Code native fields
    argument_hint: str | None = Field(default=None, alias="argument-hint")
    allowed_tools: list[str] | None = Field(default=None, alias="allowed-tools")
    model: str | None = None

    # STDD workflow fields (already in use under .agents/commands/)
    agent: str | None = None
    subtask: bool | None = None
    return_: list[str] | None = Field(default=None, alias="return")


# ---------------------------------------------------------------------------
# Hook entries (as they appear inside settings.json)
# ---------------------------------------------------------------------------


class HookCommand(BaseModel):
    type: Literal["command"]
    command: str
    timeout: int | None = Field(default=None, ge=1)


class HookMatcher(BaseModel):
    """One matcher block under PreToolUse / PostToolUse / etc."""

    matcher: str = ""  # regex over tool names; empty = match-all
    hooks: list[HookCommand]


# ---------------------------------------------------------------------------
# Phase + Workflow manifests
# ---------------------------------------------------------------------------


class PhaseConstraints(BaseModel):
    model_config = ConfigDict(extra="allow")

    write_access: str | bool = True
    bash_scope: str | None = None
    external_apis: list[str] = Field(default_factory=list)
    require_approval: bool = False


class ConvergenceSpec(BaseModel):
    max_iterations: int = Field(default=1, ge=1)
    convergence_rule: str | None = None  # e.g. "same_findings_twice"
    escalation_rule: str | None = None  # e.g. "if_issues_found_escalate_to_human"


class OutputGate(BaseModel):
    model_config = ConfigDict(extra="allow")

    validation: str | None = None
    file_pattern_check: str | None = None
    coverage_threshold: str | None = None
    approval_rule: str | None = None


class PhaseManifest(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    driver: str  # agent name
    workers: list[str] = Field(default_factory=list)
    parallel: bool = False
    skills: list[str] = Field(default_factory=list)  # glob patterns
    constraints: PhaseConstraints | None = None
    convergence: ConvergenceSpec | None = None
    output_gate: OutputGate | None = None
    produces: list[str] = Field(default_factory=list)
    requires: list[str] = Field(default_factory=list)
    extensions: dict[str, Any] = Field(default_factory=dict)


class WorkflowManifest(BaseModel):
    """Root manifest (workflow.yaml) for a workflow plugin."""

    model_config = ConfigDict(extra="allow")

    name: SkillName
    description: Annotated[str, StringConstraints(min_length=1, max_length=1024)]
    version: SemVer
    runtime_min_version: SemVer
    phases: list[PhaseManifest]

    @field_validator("phases")
    @classmethod
    def phases_not_empty(cls, v: list[PhaseManifest]) -> list[PhaseManifest]:
        if not v:
            raise ValueError("workflow must declare at least one phase")
        return v

    @model_validator(mode="after")
    def phase_names_unique(self) -> WorkflowManifest:
        seen: set[str] = set()
        for p in self.phases:
            if p.name in seen:
                raise ValueError(f"duplicate phase name: {p.name!r}")
            seen.add(p.name)
        return self


__all__ = [
    "Agent",
    "Command",
    "ConvergenceSpec",
    "HookCommand",
    "HookMatcher",
    "OutputGate",
    "PermissionValue",
    "Permissions",
    "PhaseConstraints",
    "PhaseManifest",
    "SemVer",
    "Skill",
    "SkillName",
    "WorkflowManifest",
]
