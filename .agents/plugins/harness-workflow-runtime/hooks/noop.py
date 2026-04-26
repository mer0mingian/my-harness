#!/usr/bin/env python3
"""Phase 1 no-op PreToolUse hook.

Purpose: prove the plugin's hook wiring reaches Claude Code. Does not enforce
anything. Phase 4 replaces this script with the real allow/deny logic reading
the workflow state file.

Behaviour:
  * Silent by default (exit 0, no output).
  * When $HARNESS_WORKFLOW_TRACE is set (any non-empty value), writes a single
    line to stderr so the smoke test can confirm the hook fires.

Always exits 0 — never blocks the tool call.
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    if os.environ.get("HARNESS_WORKFLOW_TRACE"):
        print(
            "[harness-workflow-runtime] PreToolUse fired (Phase 1 noop)",
            file=sys.stderr,
        )
    # Claude Code PreToolUse hooks receive JSON on stdin in later phases; we
    # ignore it here. Exit 0 = allow. Exit 2 + stderr = deny (Phase 4 surface).
    return 0


if __name__ == "__main__":
    sys.exit(main())
