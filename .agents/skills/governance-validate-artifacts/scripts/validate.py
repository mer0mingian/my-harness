#!/usr/bin/env python3
"""Validate Phase 0 governance artifacts.

Usage:
    python validate.py [--root REPO_ROOT]

Checks the three governance artifacts under ``docs/governance/`` against the
JSON schemas in ``.agents/schemas/governance/`` plus structural rules
documented in ``governance-validate-artifacts/SKILL.md``.

Exit codes:
    0 - all artifacts pass.
    1 - one or more errors. (Warnings are reported but do not affect exit code.)
    2 - artifact missing or unreadable.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


EARS_KEYWORDS = ("shall", "when", "while", "where", "if ", "if,")
NFR_ID_RE = re.compile(r"NFR-(PERF|REL|SEC|USE|MAIN|COMP|PORT|FUNC)-\d{3}")
JOURNEY_ID_RE = re.compile(r"\b[A-Z]+-\d{3}\b")
PRIORITY_VALUES = {"P0", "P1", "P2"}


@dataclass
class Finding:
    file: str
    rule: str
    location: str
    message: str
    severity: str  # "error" | "warning"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def error(self, **kw: str) -> None:
        self.findings.append(Finding(severity="error", **kw))

    def warning(self, **kw: str) -> None:
        self.findings.append(Finding(severity="warning", **kw))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warning"]


def _read(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def validate_constitution(path: Path, report: Report) -> None:
    text = _read(path)
    if text is None:
        report.error(
            file=str(path),
            rule="file_present",
            location="-",
            message="TECHNICAL_CONSTITUTION.md is missing or unreadable.",
        )
        return

    required = (
        "## 1. Technology Preferences",
        "## 2. Solution Approach Constraints",
        "## 3. Code Quality Standards",
        "## 4. Security Baseline",
        "## 5. Amendment Process",
    )
    for heading in required:
        if heading not in text:
            report.error(
                file=str(path),
                rule="required_section",
                location=heading,
                message=f"Required section missing: '{heading}'.",
            )

    for header_field in ("Version:", "Last Updated:", "Governance:"):
        if header_field not in text:
            report.error(
                file=str(path),
                rule="header_field",
                location="header",
                message=f"Header field missing: '{header_field}'.",
            )

    # Rationale check: every MUST/MUST NOT line should have nearby "Rationale" or "TBD".
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.search(r"\b(MUST|MUST NOT)\b", line) and "**" not in line and not line.startswith("#"):
            window = "\n".join(lines[i : i + 8]).lower()
            if "rationale" not in window and "tbd" not in window:
                report.warning(
                    file=str(path),
                    rule="rationale_missing",
                    location=f"line {i + 1}: {line.strip()[:80]}",
                    message="MUST/MUST NOT line has no nearby Rationale or TBD marker.",
                )


def validate_nfr_catalog(path: Path, report: Report) -> None:
    text = _read(path)
    if text is None:
        report.error(
            file=str(path),
            rule="file_present",
            location="-",
            message="NFR_CATALOG.md is missing or unreadable.",
        )
        return

    blocks = re.split(r"^### (NFR-[A-Z]+-\d{3}[^\n]*)$", text, flags=re.MULTILINE)
    seen_ids: set[str] = set()
    # blocks structure: [preamble, id_line, body, id_line, body, ...]
    for i in range(1, len(blocks), 2):
        id_line = blocks[i].strip()
        body = blocks[i + 1] if i + 1 < len(blocks) else ""
        match = NFR_ID_RE.search(id_line)
        if not match:
            report.error(
                file=str(path),
                rule="nfr_id_pattern",
                location=id_line,
                message="NFR ID does not match pattern NFR-<CATEGORY>-NNN.",
            )
            continue
        nfr_id = match.group(0)
        if nfr_id in seen_ids:
            report.error(
                file=str(path),
                rule="nfr_id_unique",
                location=nfr_id,
                message="Duplicate NFR ID.",
            )
        seen_ids.add(nfr_id)

        for required_field in (
            "**Category:**",
            "**Requirement (EARS):**",
            "**Acceptance Criteria:**",
            "**Test Strategy:**",
            "**Priority:**",
        ):
            if required_field not in body:
                report.error(
                    file=str(path),
                    rule="nfr_required_field",
                    location=nfr_id,
                    message=f"NFR block missing field: {required_field}.",
                )

        ears_block = re.search(
            r"\*\*Requirement \(EARS\):\*\*\s*\n>\s*(.+?)(?:\n\n|\Z)",
            body,
            flags=re.DOTALL,
        )
        if ears_block:
            statement = ears_block.group(1).lower()
            if not any(kw in statement for kw in EARS_KEYWORDS):
                report.error(
                    file=str(path),
                    rule="ears_keyword_required",
                    location=nfr_id,
                    message="Requirement statement contains no EARS keyword (shall/when/while/where/if).",
                )

        priority_match = re.search(r"\*\*Priority:\*\*\s*(\S+)", body)
        if priority_match:
            priority = priority_match.group(1).strip().rstrip(".")
            if priority not in PRIORITY_VALUES:
                report.error(
                    file=str(path),
                    rule="priority_value",
                    location=nfr_id,
                    message=f"Priority must be one of P0/P1/P2, got '{priority}'.",
                )

    if not seen_ids:
        report.error(
            file=str(path),
            rule="nfr_count",
            location="-",
            message="No NFR blocks found.",
        )


def validate_test_strategy(path: Path, report: Report) -> None:
    text = _read(path)
    if text is None:
        report.error(
            file=str(path),
            rule="file_present",
            location="-",
            message="TEST_STRATEGY.md is missing or unreadable.",
        )
        return

    required_sections = (
        "Test Pyramid",
        "E2E Test Scope",
        "Playwright Implementation Patterns",
        "Visual Regression",
        "Test Data Strategy",
        "CI/CD Integration",
        "Metrics",
        "Test Maintenance",
    )
    for section in required_sections:
        if section not in text:
            report.error(
                file=str(path),
                rule="required_section",
                location=section,
                message=f"Required section missing: '{section}'.",
            )

    # Pyramid totals.
    ratios = re.findall(r"\b(\d{1,3})\s*%", text)
    if ratios:
        # Heuristic: take the first three % values that are <= 100.
        nums = [int(r) for r in ratios if int(r) <= 100][:3]
        if len(nums) == 3 and sum(nums) != 100:
            report.warning(
                file=str(path),
                rule="pyramid_sum",
                location="Test Pyramid",
                message=f"Pyramid ratios sum to {sum(nums)}, expected 100.",
            )

    if "time.sleep" not in text:
        report.warning(
            file=str(path),
            rule="forbid_time_sleep",
            location="Playwright section",
            message="Strategy should explicitly forbid time.sleep().",
        )
    if "Page Object" not in text and "POM" not in text:
        report.error(
            file=str(path),
            rule="pom_required",
            location="Playwright section",
            message="Strategy must mandate the Page Object Model.",
        )


def cross_reference_checks(root: Path, report: Report) -> None:
    nfr_path = root / "docs" / "governance" / "NFR_CATALOG.md"
    strategy_path = root / "docs" / "governance" / "TEST_STRATEGY.md"
    nfr_text = _read(nfr_path) or ""
    strategy_text = _read(strategy_path) or ""
    nfr_ids = set(m.group(0) for m in NFR_ID_RE.finditer(nfr_text))

    referenced = set(m.group(0) for m in NFR_ID_RE.finditer(strategy_text))
    missing = referenced - nfr_ids
    for nid in sorted(missing):
        report.error(
            file=str(strategy_path),
            rule="cross_reference",
            location=nid,
            message=f"TEST_STRATEGY references {nid} which does not exist in NFR_CATALOG.",
        )


def render(report: Report) -> str:
    lines = []
    overall = "FAIL" if report.errors else ("WARN" if report.warnings else "PASS")
    lines.append(f"overall: {overall}")
    lines.append(f"errors: {len(report.errors)}")
    lines.append(f"warnings: {len(report.warnings)}")
    for f in report.findings:
        lines.append(
            f"- [{f.severity.upper()}] {f.file}::{f.rule} @ {f.location} - {f.message}"
        )
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root containing docs/governance/ (default: cwd).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.root).resolve()
    gov = root / "docs" / "governance"
    report = Report()

    validate_constitution(gov / "TECHNICAL_CONSTITUTION.md", report)
    validate_nfr_catalog(gov / "NFR_CATALOG.md", report)
    validate_test_strategy(gov / "TEST_STRATEGY.md", report)
    cross_reference_checks(root, report)

    print(render(report))

    if any(f.rule == "file_present" for f in report.errors):
        return 2
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
