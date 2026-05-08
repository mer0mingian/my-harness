#!/usr/bin/env python3
"""Unit tests for scripts/detect_review_convergence.py — S8-004.

Tests convergence detection logic and review.md integration.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

# Path to the script under test
SCRIPT = Path(__file__).parent.parent.parent / "scripts" / "detect_review_convergence.py"
REVIEW_MD = Path(__file__).parent.parent.parent / "commands" / "review.md"


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

def _make_artifact(tmp_path: Path, name: str, findings: list[str]) -> Path:
    """Write a review artifact with a ## Findings section."""
    lines = ["# Review Artifact", "", "## Findings", ""]
    for finding in findings:
        lines.append(finding)
    lines.append("")
    lines.append("## Other Section")
    lines.append("Some other content.")
    path = tmp_path / name
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _run_script(*args: str) -> subprocess.CompletedProcess:
    """Run detect_review_convergence.py with given positional args."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Import the script module for unit-level testing
# ---------------------------------------------------------------------------

sys.path.insert(0, str(SCRIPT.parent))
from detect_review_convergence import (
    extract_findings,
    hash_findings,
    load_and_hash,
    detect_convergence,
)


# ---------------------------------------------------------------------------
# extract_findings — unit tests
# ---------------------------------------------------------------------------

class TestExtractFindings:
    """Tests for finding extraction from ## Findings section."""

    def test_extracts_bullet_dash_lines(self):
        content = "# Title\n\n## Findings\n\n- finding one\n- finding two\n\n## Other\n"
        result = extract_findings(content)
        assert "- finding one" in result
        assert "- finding two" in result

    def test_extracts_bullet_asterisk_lines(self):
        content = "# Title\n\n## Findings\n\n* finding star\n* another\n\n## Other\n"
        result = extract_findings(content)
        assert "* finding star" in result
        assert "* another" in result

    def test_ignores_lines_outside_findings_section(self):
        content = "# Title\n- not a finding\n\n## Findings\n\n- real finding\n\n## Other\n- outside\n"
        result = extract_findings(content)
        assert "- real finding" in result
        assert "- not a finding" not in result
        assert "- outside" not in result

    def test_returns_empty_list_when_no_findings_section(self):
        content = "# Title\n\n## Summary\n\n- something\n"
        result = extract_findings(content)
        assert result == []

    def test_returns_empty_list_for_empty_findings_section(self):
        content = "# Title\n\n## Findings\n\n## Other\n"
        result = extract_findings(content)
        assert result == []

    def test_findings_are_sorted(self):
        content = "# Title\n\n## Findings\n\n- beta\n- alpha\n- gamma\n"
        result = extract_findings(content)
        assert result == sorted(result)

    def test_stops_at_next_heading(self):
        content = "# Title\n\n## Findings\n\n- finding\n\n## Verdict\n\n- not finding\n"
        result = extract_findings(content)
        assert len(result) == 1
        assert "- finding" in result


# ---------------------------------------------------------------------------
# hash_findings — unit tests
# ---------------------------------------------------------------------------

class TestHashFindings:
    """Tests for SHA256 hashing of combined finding sets."""

    def test_hash_is_sha256_hex(self):
        result = hash_findings(["- finding one"])
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_same_findings_same_hash(self):
        h1 = hash_findings(["- a", "- b"])
        h2 = hash_findings(["- a", "- b"])
        assert h1 == h2

    def test_different_findings_different_hash(self):
        h1 = hash_findings(["- a"])
        h2 = hash_findings(["- b"])
        assert h1 != h2

    def test_empty_findings_has_stable_hash(self):
        h = hash_findings([])
        expected = hashlib.sha256("".encode("utf-8")).hexdigest()
        assert h == expected

    def test_hash_combines_arch_and_code_findings(self):
        """Hash is computed over both arch and code findings joined."""
        arch = ["- arch finding"]
        code = ["- code finding"]
        # Combined means both sets contribute
        combined = sorted(arch) + sorted(code)
        joined = "\n".join(combined)
        expected = hashlib.sha256(joined.encode("utf-8")).hexdigest()
        actual = hash_findings(arch, code)
        assert actual == expected


# ---------------------------------------------------------------------------
# detect_convergence — unit tests
# ---------------------------------------------------------------------------

class TestDetectConvergence:
    """Tests for the convergence comparison logic."""

    def test_same_findings_returns_converged_true(self, tmp_path):
        arch1 = _make_artifact(tmp_path, "arch1.md", ["- finding A", "- finding B"])
        code1 = _make_artifact(tmp_path, "code1.md", ["- code finding"])
        arch2 = _make_artifact(tmp_path, "arch2.md", ["- finding A", "- finding B"])
        code2 = _make_artifact(tmp_path, "code2.md", ["- code finding"])

        result = detect_convergence(arch1, code1, arch2, code2)
        assert result["converged"] is True

    def test_different_findings_returns_converged_false(self, tmp_path):
        arch1 = _make_artifact(tmp_path, "arch1.md", ["- finding A"])
        code1 = _make_artifact(tmp_path, "code1.md", ["- code finding"])
        arch2 = _make_artifact(tmp_path, "arch2.md", ["- finding B (new)"])
        code2 = _make_artifact(tmp_path, "code2.md", ["- code finding"])

        result = detect_convergence(arch1, code1, arch2, code2)
        assert result["converged"] is False

    def test_result_contains_current_hash(self, tmp_path):
        arch1 = _make_artifact(tmp_path, "arch1.md", ["- finding A"])
        code1 = _make_artifact(tmp_path, "code1.md", [])
        arch2 = _make_artifact(tmp_path, "arch2.md", ["- finding B"])
        code2 = _make_artifact(tmp_path, "code2.md", [])

        result = detect_convergence(arch1, code1, arch2, code2)
        assert "current_hash" in result
        assert len(result["current_hash"]) == 64

    def test_result_contains_previous_hash(self, tmp_path):
        arch1 = _make_artifact(tmp_path, "arch1.md", ["- finding A"])
        code1 = _make_artifact(tmp_path, "code1.md", [])
        arch2 = _make_artifact(tmp_path, "arch2.md", ["- finding B"])
        code2 = _make_artifact(tmp_path, "code2.md", [])

        result = detect_convergence(arch1, code1, arch2, code2)
        assert "previous_hash" in result
        assert len(result["previous_hash"]) == 64

    def test_result_contains_reason(self, tmp_path):
        arch1 = _make_artifact(tmp_path, "arch1.md", ["- finding"])
        code1 = _make_artifact(tmp_path, "code1.md", [])
        arch2 = _make_artifact(tmp_path, "arch2.md", ["- finding"])
        code2 = _make_artifact(tmp_path, "code2.md", [])

        result = detect_convergence(arch1, code1, arch2, code2)
        assert "reason" in result
        assert isinstance(result["reason"], str)


# ---------------------------------------------------------------------------
# CLI integration — subprocess tests
# ---------------------------------------------------------------------------

class TestCLITwoArgs:
    """First run: 2 args → always not converged (no baseline)."""

    def test_two_args_exits_1(self, tmp_path):
        arch = _make_artifact(tmp_path, "arch.md", ["- finding"])
        code = _make_artifact(tmp_path, "code.md", ["- code finding"])

        proc = _run_script(str(arch), str(code))
        assert proc.returncode == 1

    def test_two_args_outputs_json(self, tmp_path):
        arch = _make_artifact(tmp_path, "arch.md", ["- finding"])
        code = _make_artifact(tmp_path, "code.md", [])

        proc = _run_script(str(arch), str(code))
        data = json.loads(proc.stdout)
        assert "converged" in data
        assert data["converged"] is False

    def test_two_args_reason_mentions_no_baseline(self, tmp_path):
        arch = _make_artifact(tmp_path, "arch.md", ["- finding"])
        code = _make_artifact(tmp_path, "code.md", [])

        proc = _run_script(str(arch), str(code))
        data = json.loads(proc.stdout)
        reason = data["reason"].lower()
        assert "no" in reason or "baseline" in reason or "previous" in reason


class TestCLIFourArgs:
    """Four args: compare current vs previous."""

    def test_same_findings_exits_0(self, tmp_path):
        arch_curr = _make_artifact(tmp_path, "arch_curr.md", ["- same finding"])
        code_curr = _make_artifact(tmp_path, "code_curr.md", ["- code same"])
        arch_prev = _make_artifact(tmp_path, "arch_prev.md", ["- same finding"])
        code_prev = _make_artifact(tmp_path, "code_prev.md", ["- code same"])

        proc = _run_script(str(arch_curr), str(code_curr), str(arch_prev), str(code_prev))
        assert proc.returncode == 0

    def test_same_findings_json_converged_true(self, tmp_path):
        arch_curr = _make_artifact(tmp_path, "arch_curr.md", ["- finding A", "- finding B"])
        code_curr = _make_artifact(tmp_path, "code_curr.md", ["- code"])
        arch_prev = _make_artifact(tmp_path, "arch_prev.md", ["- finding A", "- finding B"])
        code_prev = _make_artifact(tmp_path, "code_prev.md", ["- code"])

        proc = _run_script(str(arch_curr), str(code_curr), str(arch_prev), str(code_prev))
        data = json.loads(proc.stdout)
        assert data["converged"] is True

    def test_different_findings_exits_1(self, tmp_path):
        arch_curr = _make_artifact(tmp_path, "arch_curr.md", ["- new finding"])
        code_curr = _make_artifact(tmp_path, "code_curr.md", [])
        arch_prev = _make_artifact(tmp_path, "arch_prev.md", ["- old finding"])
        code_prev = _make_artifact(tmp_path, "code_prev.md", [])

        proc = _run_script(str(arch_curr), str(code_curr), str(arch_prev), str(code_prev))
        assert proc.returncode == 1

    def test_different_findings_json_converged_false(self, tmp_path):
        arch_curr = _make_artifact(tmp_path, "arch_curr.md", ["- new finding"])
        code_curr = _make_artifact(tmp_path, "code_curr.md", [])
        arch_prev = _make_artifact(tmp_path, "arch_prev.md", ["- old finding"])
        code_prev = _make_artifact(tmp_path, "code_prev.md", [])

        proc = _run_script(str(arch_curr), str(code_curr), str(arch_prev), str(code_prev))
        data = json.loads(proc.stdout)
        assert data["converged"] is False

    def test_both_empty_findings_exits_0(self, tmp_path):
        """Empty findings on both sides = converged (hashes match)."""
        arch_curr = _make_artifact(tmp_path, "arch_curr.md", [])
        code_curr = _make_artifact(tmp_path, "code_curr.md", [])
        arch_prev = _make_artifact(tmp_path, "arch_prev.md", [])
        code_prev = _make_artifact(tmp_path, "code_prev.md", [])

        proc = _run_script(str(arch_curr), str(code_curr), str(arch_prev), str(code_prev))
        assert proc.returncode == 0

    def test_both_empty_findings_json_has_matching_hashes(self, tmp_path):
        """Both empty means current_hash == previous_hash."""
        arch_curr = _make_artifact(tmp_path, "arch_curr.md", [])
        code_curr = _make_artifact(tmp_path, "code_curr.md", [])
        arch_prev = _make_artifact(tmp_path, "arch_prev.md", [])
        code_prev = _make_artifact(tmp_path, "code_prev.md", [])

        proc = _run_script(str(arch_curr), str(code_curr), str(arch_prev), str(code_prev))
        data = json.loads(proc.stdout)
        assert data["current_hash"] == data["previous_hash"]

    def test_output_is_valid_json(self, tmp_path):
        arch_curr = _make_artifact(tmp_path, "arch_curr.md", ["- a"])
        code_curr = _make_artifact(tmp_path, "code_curr.md", [])
        arch_prev = _make_artifact(tmp_path, "arch_prev.md", ["- a"])
        code_prev = _make_artifact(tmp_path, "code_prev.md", [])

        proc = _run_script(str(arch_curr), str(code_curr), str(arch_prev), str(code_prev))
        data = json.loads(proc.stdout)
        assert "converged" in data
        assert "reason" in data
        assert "current_hash" in data
        assert "previous_hash" in data


class TestCLIFileNotFound:
    """Missing file arguments → exit 2."""

    def test_missing_arch_file_exits_2(self, tmp_path):
        code = _make_artifact(tmp_path, "code.md", [])
        proc = _run_script("/nonexistent/arch.md", str(code))
        assert proc.returncode == 2

    def test_missing_code_file_exits_2(self, tmp_path):
        arch = _make_artifact(tmp_path, "arch.md", [])
        proc = _run_script(str(arch), "/nonexistent/code.md")
        assert proc.returncode == 2

    def test_missing_prev_arch_exits_2(self, tmp_path):
        arch = _make_artifact(tmp_path, "arch.md", [])
        code = _make_artifact(tmp_path, "code.md", [])
        proc = _run_script(str(arch), str(code), "/nonexistent/prev_arch.md", str(code))
        assert proc.returncode == 2

    def test_file_not_found_outputs_json_with_error(self, tmp_path):
        code = _make_artifact(tmp_path, "code.md", [])
        proc = _run_script("/nonexistent/arch.md", str(code))
        data = json.loads(proc.stdout)
        assert "error" in data or "reason" in data


# ---------------------------------------------------------------------------
# review.md content tests
# ---------------------------------------------------------------------------

class TestReviewMdStep1ConvergenceDetection:
    """Step 1 must list gates.convergence_detection config key."""

    @pytest.fixture
    def review_md_content(self) -> str:
        assert REVIEW_MD.exists(), f"commands/review.md not found at {REVIEW_MD}"
        return REVIEW_MD.read_text()

    def test_step1_mentions_convergence_detection(self, review_md_content):
        """Step 1 must list convergence_detection as a loaded config key."""
        assert "convergence_detection" in review_md_content, (
            "commands/review.md must reference 'convergence_detection' config key"
        )

    def test_step1_section_contains_convergence_detection(self, review_md_content):
        """The Load Configuration section must mention convergence_detection."""
        step1_start = review_md_content.find("## Step 1:")
        assert step1_start != -1, "Step 1 section not found in review.md"

        step2_start = review_md_content.find("## Step 2:", step1_start)
        assert step2_start != -1, "Step 2 section not found in review.md"

        step1_content = review_md_content[step1_start:step2_start]
        assert "convergence_detection" in step1_content, (
            "Step 1 (Load Configuration) must reference 'gates.convergence_detection'. "
            f"Step 1 content:\n{step1_content}"
        )

    def test_step1_convergence_detection_default_false(self, review_md_content):
        """Step 1 must document that convergence_detection defaults to false."""
        step1_start = review_md_content.find("## Step 1:")
        step2_start = review_md_content.find("## Step 2:", step1_start)
        step1_content = review_md_content[step1_start:step2_start]

        has_default_false = (
            "convergence_detection" in step1_content
            and "false" in step1_content
        )
        assert has_default_false, (
            "review.md Step 1 must document that convergence_detection defaults to false. "
            f"Step 1 content:\n{step1_content}"
        )


class TestReviewMdStep9ConvergenceCheck:
    """Step 9 must include convergence check instruction."""

    @pytest.fixture
    def review_md_content(self) -> str:
        assert REVIEW_MD.exists(), f"commands/review.md not found at {REVIEW_MD}"
        return REVIEW_MD.read_text()

    def _get_step9_content(self, review_md_content: str) -> str:
        step9_start = review_md_content.find("## Step 9:")
        assert step9_start != -1, "Step 9 section not found in review.md"
        step10_start = review_md_content.find("## Step 10:", step9_start)
        assert step10_start != -1, "Step 10 section not found in review.md"
        return review_md_content[step9_start:step10_start]

    def test_step9_has_convergence_check(self, review_md_content):
        """Step 9 must mention detect_review_convergence."""
        step9 = self._get_step9_content(review_md_content)
        assert "detect_review_convergence" in step9, (
            "Step 9 must reference 'detect_review_convergence' script. "
            f"Step 9 content:\n{step9}"
        )

    def test_step9_conditional_on_convergence_detection_gate(self, review_md_content):
        """Step 9 convergence check must be gated on convergence_detection config."""
        step9 = self._get_step9_content(review_md_content)
        assert "convergence_detection" in step9, (
            "Step 9 convergence check must reference the gates.convergence_detection config key. "
            f"Step 9 content:\n{step9}"
        )

    def test_step9_handles_exit_0_converged(self, review_md_content):
        """Step 9 must describe exit 0 (converged) → stop cycling."""
        step9 = self._get_step9_content(review_md_content)
        has_stop = (
            "exit 0" in step9.lower()
            or "converged" in step9.lower()
            or "stop" in step9.lower()
        )
        assert has_stop, (
            "Step 9 must describe stopping when convergence detected (exit 0). "
            f"Step 9 content:\n{step9}"
        )

    def test_step9_handles_exit_1_not_converged(self, review_md_content):
        """Step 9 must describe exit 1 (not converged) → continue cycling."""
        step9 = self._get_step9_content(review_md_content)
        has_continue = (
            "exit 1" in step9.lower()
            or "continue" in step9.lower()
            or "next cycle" in step9.lower()
        )
        assert has_continue, (
            "Step 9 must describe continuing when not converged (exit 1). "
            f"Step 9 content:\n{step9}"
        )

    def test_step9_mentions_previous_cycle_artifacts(self, review_md_content):
        """Step 9 must mention using previous cycle artifacts for comparison."""
        step9 = self._get_step9_content(review_md_content)
        has_prev = (
            "previous" in step9.lower()
            or "prev" in step9.lower()
            or "prior" in step9.lower()
        )
        assert has_prev, (
            "Step 9 must mention using previous cycle artifacts for convergence comparison. "
            f"Step 9 content:\n{step9}"
        )
