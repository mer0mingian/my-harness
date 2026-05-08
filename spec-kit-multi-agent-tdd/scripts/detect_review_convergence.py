#!/usr/bin/env python3
"""Review convergence detection helper.

Compares findings from two consecutive review cycles to determine whether
the review has converged (findings are identical) or is still evolving.

Usage:
    python3 scripts/detect_review_convergence.py <arch_review_path> <code_review_path>
    python3 scripts/detect_review_convergence.py <arch_review_path> <code_review_path> \\
        <prev_arch_review_path> <prev_code_review_path>

With 2 args: first run, no previous baseline — always exits 1 (not converged).
With 4 args: compare current pair vs previous pair.

Algorithm:
    1. Extract all bullet points (lines starting with `- ` or `* `) from
       the `## Findings` section of each artifact.
    2. Sort findings, join with newlines, SHA256 hash.
    3. If hash(current_arch + current_code) == hash(prev_arch + prev_code) → converged.
    4. Output JSON: {"converged": bool, "reason": str,
                     "current_hash": str, "previous_hash": str}

Exit Codes:
    0: Converged (stop cycling)
    1: Not converged (continue) — includes first-run / no baseline
    2: Error (file not found, unreadable)
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def extract_findings(content: str) -> list[str]:
    """Extract sorted bullet-point findings from the ## Findings section.

    Args:
        content: Full text of a review artifact.

    Returns:
        Sorted list of finding lines (lines starting with '- ' or '* ').
        Returns empty list if no ## Findings section is present.
    """
    findings: list[str] = []
    in_findings = False

    for line in content.splitlines():
        stripped = line.strip()

        # Detect ## Findings heading (case-sensitive per spec)
        if stripped == "## Findings":
            in_findings = True
            continue

        # Stop at next ## heading
        if in_findings and stripped.startswith("## "):
            break

        # Collect bullet lines
        if in_findings and (stripped.startswith("- ") or stripped.startswith("* ")):
            findings.append(stripped)

    return sorted(findings)


def hash_findings(
    arch_findings: list[str],
    code_findings: Optional[list[str]] = None,
) -> str:
    """Compute SHA256 hash of combined finding sets.

    Args:
        arch_findings: Sorted findings from the architecture review.
        code_findings: Sorted findings from the code review (optional).

    Returns:
        Lowercase hex SHA256 digest string.
    """
    if code_findings is None:
        code_findings = []

    combined = sorted(arch_findings) + sorted(code_findings)
    joined = "\n".join(combined)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def load_and_hash(arch_path: Path, code_path: Path) -> tuple[str, str, str]:
    """Read two review artifacts and compute their combined hash.

    Args:
        arch_path: Path to architecture review artifact.
        code_path: Path to code review artifact.

    Returns:
        Tuple of (arch_text, code_text, combined_hash).

    Raises:
        FileNotFoundError: If either file does not exist.
    """
    arch_text = arch_path.read_text(encoding="utf-8")
    code_text = code_path.read_text(encoding="utf-8")
    arch_findings = extract_findings(arch_text)
    code_findings = extract_findings(code_text)
    combined_hash = hash_findings(arch_findings, code_findings)
    return arch_text, code_text, combined_hash


def detect_convergence(
    curr_arch: Path,
    curr_code: Path,
    prev_arch: Path,
    prev_code: Path,
) -> dict:
    """Compare current and previous review cycle artifacts for convergence.

    Args:
        curr_arch: Current cycle architecture review path.
        curr_code: Current cycle code review path.
        prev_arch: Previous cycle architecture review path.
        prev_code: Previous cycle code review path.

    Returns:
        Dict with keys: converged (bool), reason (str),
        current_hash (str), previous_hash (str).
    """
    _, _, current_hash = load_and_hash(curr_arch, curr_code)
    _, _, previous_hash = load_and_hash(prev_arch, prev_code)

    converged = current_hash == previous_hash
    if converged:
        reason = "Findings are identical to previous cycle — convergence detected."
    else:
        reason = "Findings differ from previous cycle — review is still evolving."

    return {
        "converged": converged,
        "reason": reason,
        "current_hash": current_hash,
        "previous_hash": previous_hash,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """CLI entry point.

    Returns:
        0 = converged, 1 = not converged, 2 = error
    """
    parser = argparse.ArgumentParser(
        description="Detect convergence between consecutive review cycles",
        epilog=(
            "Exit codes: 0=converged (stop), 1=not converged (continue), "
            "2=error (file not found)"
        ),
    )
    parser.add_argument("arch_review", help="Current cycle arch review path")
    parser.add_argument("code_review", help="Current cycle code review path")
    parser.add_argument(
        "prev_arch_review",
        nargs="?",
        default=None,
        help="Previous cycle arch review path (omit for first run)",
    )
    parser.add_argument(
        "prev_code_review",
        nargs="?",
        default=None,
        help="Previous cycle code review path (omit for first run)",
    )

    args = parser.parse_args()

    curr_arch = Path(args.arch_review)
    curr_code = Path(args.code_review)

    # --- Check current files exist ---
    missing: list[str] = []
    for p in (curr_arch, curr_code):
        if not p.exists():
            missing.append(str(p))

    # --- First-run path (2 args only) ---
    if args.prev_arch_review is None and args.prev_code_review is None:
        if missing:
            output = {
                "converged": False,
                "reason": f"File not found: {', '.join(missing)}",
                "current_hash": "",
                "previous_hash": "",
                "error": f"File not found: {', '.join(missing)}",
            }
            print(json.dumps(output, indent=2))
            return 2

        # Compute current hash for reference; no previous to compare
        try:
            _, _, current_hash = load_and_hash(curr_arch, curr_code)
        except OSError as exc:
            output = {
                "converged": False,
                "reason": str(exc),
                "current_hash": "",
                "previous_hash": "",
                "error": str(exc),
            }
            print(json.dumps(output, indent=2))
            return 2

        output = {
            "converged": False,
            "reason": "No previous baseline — first run, cannot determine convergence.",
            "current_hash": current_hash,
            "previous_hash": "",
        }
        print(json.dumps(output, indent=2))
        return 1

    # --- Four-arg comparison path ---
    prev_arch = Path(args.prev_arch_review)
    prev_code = Path(args.prev_code_review)

    for p in (prev_arch, prev_code):
        if not p.exists():
            missing.append(str(p))

    if missing:
        output = {
            "converged": False,
            "reason": f"File not found: {', '.join(missing)}",
            "current_hash": "",
            "previous_hash": "",
            "error": f"File not found: {', '.join(missing)}",
        }
        print(json.dumps(output, indent=2))
        return 2

    try:
        result = detect_convergence(curr_arch, curr_code, prev_arch, prev_code)
    except OSError as exc:
        output = {
            "converged": False,
            "reason": str(exc),
            "current_hash": "",
            "previous_hash": "",
            "error": str(exc),
        }
        print(json.dumps(output, indent=2))
        return 2

    print(json.dumps(result, indent=2))
    return 0 if result["converged"] else 1


if __name__ == "__main__":
    sys.exit(main())
