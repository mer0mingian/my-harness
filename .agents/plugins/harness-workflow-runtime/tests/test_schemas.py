"""Smoke tests for the pydantic schema models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from harness_workflow.schemas import (
    Agent,
    Command,
    HookCommand,
    HookMatcher,
    Permissions,
    PhaseManifest,
    Skill,
    WorkflowManifest,
)


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------


class TestSkill:
    def test_minimal_valid(self) -> None:
        Skill(name="my-skill", description="A skill.")

    def test_digits_in_name(self) -> None:
        Skill(name="skill-42", description="x")

    def test_rejects_uppercase_name(self) -> None:
        with pytest.raises(ValidationError):
            Skill(name="MySkill", description="x")

    def test_rejects_underscore_name(self) -> None:
        with pytest.raises(ValidationError):
            Skill(name="my_skill", description="x")

    def test_rejects_claude_in_name(self) -> None:
        with pytest.raises(ValidationError):
            Skill(name="claude-helper", description="x")

    def test_rejects_anthropic_in_name(self) -> None:
        with pytest.raises(ValidationError):
            Skill(name="my-anthropic", description="x")

    def test_name_length_cap(self) -> None:
        with pytest.raises(ValidationError):
            Skill(name="a" * 65, description="x")

    def test_description_length_cap(self) -> None:
        with pytest.raises(ValidationError):
            Skill(name="ok", description="x" * 1025)

    def test_accepts_extra_metadata_fields(self) -> None:
        s = Skill.model_validate(
            {"name": "ok", "description": "x", "metadata": {"author": "qa"}}
        )
        assert s.metadata == {"author": "qa"}


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


class TestPermissions:
    def test_opencode_style(self) -> None:
        p = Permissions.model_validate(
            {"skill": {"stdd-*": "allow", "review-*": "allow", "": "deny"}}
        )
        assert p.style == "opencode"
        assert p.skill == {"stdd-*": "allow", "review-*": "allow", "": "deny"}

    def test_stdd_style(self) -> None:
        p = Permissions.model_validate(
            {
                "read": {"*": "allow"},
                "write": {"tests/**": "allow"},
                "edit": {"tests/**": "allow"},
                "bash": {"pytest": "allow"},
            }
        )
        assert p.style == "stdd"

    def test_rejects_invalid_permission_value(self) -> None:
        with pytest.raises(ValidationError):
            Permissions.model_validate({"skill": {"stdd-*": "maybe"}})

    def test_unknown_style_when_empty(self) -> None:
        assert Permissions().style == "unknown"


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


class TestAgent:
    def test_opencode_permission(self) -> None:
        a = Agent.model_validate(
            {
                "description": "reviewer",
                "skills": ["review-*"],
                "permission": {"skill": {"review-*": "allow"}},
            }
        )
        assert a.permission is not None
        assert a.permission.style == "opencode"

    def test_stdd_permission(self) -> None:
        a = Agent.model_validate(
            {
                "description": "stdd agent",
                "permission": {
                    "read": {"*": "allow"},
                    "write": {"test_*.py": "allow"},
                },
            }
        )
        assert a.permission is not None
        assert a.permission.style == "stdd"

    def test_no_permission_block_ok(self) -> None:
        Agent.model_validate({"description": "simple agent"})

    def test_missing_description_fails(self) -> None:
        with pytest.raises(ValidationError):
            Agent.model_validate({"skills": []})

    def test_mode_values(self) -> None:
        Agent.model_validate({"description": "x", "mode": "subagent"})
        with pytest.raises(ValidationError):
            Agent.model_validate({"description": "x", "mode": "bogus"})

    def test_temperature_range(self) -> None:
        Agent.model_validate({"description": "x", "temperature": 0.1})
        with pytest.raises(ValidationError):
            Agent.model_validate({"description": "x", "temperature": 3.0})


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


class TestCommand:
    def test_claude_native_aliases(self) -> None:
        c = Command.model_validate(
            {
                "description": "Run a workflow",
                "argument-hint": "<workflow-id>",
                "allowed-tools": ["Read", "Write"],
            }
        )
        assert c.argument_hint == "<workflow-id>"
        assert c.allowed_tools == ["Read", "Write"]

    def test_stdd_workflow_fields(self) -> None:
        c = Command.model_validate(
            {
                "description": "Stage 1",
                "agent": "some-orchestrator",
                "subtask": True,
                "return": ["/subtask {agent: x} do y"],
            }
        )
        assert c.agent == "some-orchestrator"
        assert c.subtask is True
        assert c.return_ == ["/subtask {agent: x} do y"]

    def test_description_required(self) -> None:
        with pytest.raises(ValidationError):
            Command.model_validate({"agent": "x"})


# ---------------------------------------------------------------------------
# Hook
# ---------------------------------------------------------------------------


class TestHooks:
    def test_hook_matcher_minimal(self) -> None:
        hm = HookMatcher(
            matcher="Write|Edit",
            hooks=[HookCommand(type="command", command="python hook.py")],
        )
        assert hm.matcher == "Write|Edit"
        assert hm.hooks[0].command == "python hook.py"

    def test_hook_matcher_empty_matches_all(self) -> None:
        hm = HookMatcher(hooks=[HookCommand(type="command", command="true")])
        assert hm.matcher == ""

    def test_timeout_positive(self) -> None:
        HookCommand(type="command", command="x", timeout=5)
        with pytest.raises(ValidationError):
            HookCommand(type="command", command="x", timeout=0)


# ---------------------------------------------------------------------------
# Workflow manifest
# ---------------------------------------------------------------------------


MINIMAL_WORKFLOW = {
    "name": "stdd-feat",
    "description": "feature development workflow",
    "version": "0.1.0",
    "runtime_min_version": "0.1",
    "phases": [
        {"name": "setup", "driver": "orchestrator"},
        {"name": "implement", "driver": "implementer"},
    ],
}


class TestWorkflowManifest:
    def test_minimal_valid(self) -> None:
        wm = WorkflowManifest.model_validate(MINIMAL_WORKFLOW)
        assert len(wm.phases) == 2

    def test_empty_phases_rejected(self) -> None:
        bad = {**MINIMAL_WORKFLOW, "phases": []}
        with pytest.raises(ValidationError):
            WorkflowManifest.model_validate(bad)

    def test_duplicate_phase_names_rejected(self) -> None:
        bad = {
            **MINIMAL_WORKFLOW,
            "phases": [
                {"name": "x", "driver": "a"},
                {"name": "x", "driver": "b"},
            ],
        }
        with pytest.raises(ValidationError):
            WorkflowManifest.model_validate(bad)

    def test_version_must_be_semver(self) -> None:
        bad = {**MINIMAL_WORKFLOW, "version": "not-a-version"}
        with pytest.raises(ValidationError):
            WorkflowManifest.model_validate(bad)

    def test_runtime_min_version_semver(self) -> None:
        bad = {**MINIMAL_WORKFLOW, "runtime_min_version": "v1"}
        with pytest.raises(ValidationError):
            WorkflowManifest.model_validate(bad)

    def test_phase_full_shape(self) -> None:
        phase = PhaseManifest.model_validate(
            {
                "name": "review",
                "driver": "orchestrator",
                "workers": ["reviewer-a", "reviewer-b"],
                "parallel": True,
                "skills": ["review-*"],
                "convergence": {
                    "max_iterations": 3,
                    "convergence_rule": "same_findings_twice",
                },
                "constraints": {"write_access": False, "external_apis": []},
            }
        )
        assert phase.parallel is True
        assert phase.convergence is not None
        assert phase.convergence.max_iterations == 3
