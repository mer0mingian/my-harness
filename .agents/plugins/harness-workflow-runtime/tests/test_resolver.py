"""Unit tests for the resolver (glob expansion, catalog scan, ACL emitters)."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from harness_workflow.resolver import (
    PhaseACL,
    SkillCatalog,
    compile_phase_acl,
    emit_claude_acl,
    emit_opencode_acl,
    expand_globs,
    scan_marketplace,
)
from harness_workflow.schemas import PhaseManifest, Skill


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def catalog() -> SkillCatalog:
    c = SkillCatalog()
    for name in [
        "stdd-pm-specification",
        "stdd-pm-openspec",
        "stdd-tdd",
        "stdd-openspec",
        "review-differential-review",
        "review-systematic-debugging",
        "general-git-advanced-workflows",
        "general-python-environment",
    ]:
        c.skills[name] = Skill(name=name, description=f"fixture: {name}")
    return c


# ---------------------------------------------------------------------------
# Pattern expansion
# ---------------------------------------------------------------------------


class TestExpandGlobs:
    def test_single_glob(self, catalog: SkillCatalog) -> None:
        result = expand_globs(["stdd-pm-*"], catalog)
        assert result == ["stdd-pm-openspec", "stdd-pm-specification"]

    def test_union_multiple_globs(self, catalog: SkillCatalog) -> None:
        result = expand_globs(["stdd-*", "review-*"], catalog)
        assert "stdd-tdd" in result
        assert "review-differential-review" in result
        assert "general-git-advanced-workflows" not in result

    def test_negation_removes_match(self, catalog: SkillCatalog) -> None:
        result = expand_globs(["stdd-*", "!stdd-tdd"], catalog)
        assert "stdd-tdd" not in result
        assert "stdd-openspec" in result
        assert "stdd-pm-specification" in result

    def test_negation_with_glob(self, catalog: SkillCatalog) -> None:
        result = expand_globs(["stdd-*", "!stdd-pm-*"], catalog)
        assert "stdd-tdd" in result
        assert "stdd-openspec" in result
        assert "stdd-pm-specification" not in result
        assert "stdd-pm-openspec" not in result

    def test_empty_pattern_matches_all(self, catalog: SkillCatalog) -> None:
        result = expand_globs([""], catalog)
        assert len(result) == len(catalog.skills)

    def test_trailing_hyphen_prefix(self, catalog: SkillCatalog) -> None:
        # "stdd-" should be treated as prefix == "stdd-*"
        result = expand_globs(["stdd-"], catalog)
        assert "stdd-tdd" in result
        assert "stdd-pm-specification" in result
        assert "general-python-environment" not in result

    def test_exact_match(self, catalog: SkillCatalog) -> None:
        assert expand_globs(["stdd-tdd"], catalog) == ["stdd-tdd"]

    def test_unknown_returns_empty(self, catalog: SkillCatalog) -> None:
        assert expand_globs(["nonexistent-*"], catalog) == []

    def test_empty_patterns_list(self, catalog: SkillCatalog) -> None:
        assert expand_globs([], catalog) == []

    def test_result_is_sorted(self, catalog: SkillCatalog) -> None:
        result = expand_globs(["stdd-*", "review-*"], catalog)
        assert result == sorted(result)


# ---------------------------------------------------------------------------
# Marketplace scan
# ---------------------------------------------------------------------------


class TestScanMarketplace:
    def test_empty_tree(self, tmp_path: Path) -> None:
        assert scan_marketplace(tmp_path).skills == {}

    def test_discovers_valid_skill(self, tmp_path: Path) -> None:
        d = tmp_path / "skills" / "my-skill"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            dedent(
                """\
                ---
                name: my-skill
                description: fixture skill
                ---

                Body.
                """
            )
        )
        catalog = scan_marketplace(tmp_path)
        assert "my-skill" in catalog.skills
        assert catalog.skills["my-skill"].description == "fixture skill"

    def test_skips_file_without_frontmatter(self, tmp_path: Path) -> None:
        d = tmp_path / "skills" / "bad"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("Not valid.")
        assert scan_marketplace(tmp_path).skills == {}

    def test_skips_invalid_frontmatter(self, tmp_path: Path) -> None:
        # `name: Invalid Name` violates agentskills.io naming rules
        d = tmp_path / "skills" / "bad"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            "---\nname: Invalid Name\ndescription: x\n---\n\nBody."
        )
        assert scan_marketplace(tmp_path).skills == {}

    def test_skips_bare_skill_md_at_root(self, tmp_path: Path) -> None:
        (tmp_path / "SKILL.md").write_text(
            "---\nname: bare\ndescription: x\n---\n\nBody."
        )
        assert scan_marketplace(tmp_path).skills == {}


# ---------------------------------------------------------------------------
# compile_phase_acl
# ---------------------------------------------------------------------------


class TestCompilePhaseACL:
    def test_basic_resolution(self, catalog: SkillCatalog) -> None:
        phase = PhaseManifest(
            name="review",
            driver="orchestrator",
            skills=["review-*"],
        )
        acl = compile_phase_acl(phase, catalog)
        assert acl.phase_name == "review"
        assert "review-differential-review" in acl.allowed_skills
        assert "stdd-tdd" not in acl.allowed_skills

    def test_constraints_populated(self, catalog: SkillCatalog) -> None:
        phase = PhaseManifest.model_validate(
            {
                "name": "test",
                "driver": "test-writer",
                "skills": ["stdd-*"],
                "constraints": {
                    "write_access": "test_*.py",
                    "bash_scope": "sandboxed_pytest",
                    "external_apis": [],
                },
            }
        )
        acl = compile_phase_acl(phase, catalog)
        assert acl.write_access == "test_*.py"
        assert acl.bash_scope == "sandboxed_pytest"

    def test_no_skills_yields_empty_allowed_skills(self, catalog: SkillCatalog) -> None:
        phase = PhaseManifest(name="setup", driver="orchestrator", skills=[])
        acl = compile_phase_acl(phase, catalog)
        assert acl.allowed_skills == []


# ---------------------------------------------------------------------------
# Emitters
# ---------------------------------------------------------------------------


class TestClaudeEmit:
    def test_shape(self) -> None:
        acl = PhaseACL(
            phase_name="p1",
            allowed_skills=["stdd-tdd", "review-differential-review"],
            allowed_tools=["Read", "Write"],
            bash_scope="sandboxed",
            external_apis=["linear"],
            write_access="src/**",
        )
        out = emit_claude_acl(acl)
        assert out == {
            "phase": "p1",
            "allowed_skills": ["stdd-tdd", "review-differential-review"],
            "allowed_tools": ["Read", "Write"],
            "bash_scope": "sandboxed",
            "external_apis": ["linear"],
            "write_access": "src/**",
        }

    def test_no_allowed_tools_becomes_empty_list(self) -> None:
        acl = PhaseACL(
            phase_name="p1",
            allowed_skills=[],
            allowed_tools=None,
        )
        out = emit_claude_acl(acl)
        assert out["allowed_tools"] == []


class TestOpenCodeEmit:
    def test_allow_skills_plus_deny_default(self) -> None:
        acl = PhaseACL(
            phase_name="p1",
            allowed_skills=["stdd-tdd", "review-differential-review"],
            allowed_tools=None,
        )
        out = emit_opencode_acl(acl)
        assert out["stdd-tdd"] == "allow"
        assert out["review-differential-review"] == "allow"
        assert out[""] == "deny"

    def test_empty_skills_yields_only_deny_default(self) -> None:
        acl = PhaseACL(phase_name="p1", allowed_skills=[], allowed_tools=None)
        out = emit_opencode_acl(acl)
        assert out == {"": "deny"}
