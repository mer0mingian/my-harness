---
description: "Validate all Phase 0 governance artifacts against schemas, EARS rules, and cross-references."
agent: governance-lead
subtask: true
return:
  - /subtask {agent: governance-lead && as: gov_validate_run} Run the governance-validate-artifacts skill against the repository. Invoke `python .agents/skills/governance-validate-artifacts/scripts/validate.py --root .` if available, otherwise replicate the same checks inline. Return the structured findings (errors and warnings) plus the overall status (PASS / WARN / FAIL).

  - "Governance validation complete. Status: $RESULT[gov_validate_run].overall. See findings above. If FAIL, fix the listed errors before transitioning to BMAD Phase 1. WARN findings are advisory."
---
# Validate Governance Artifacts

Runs schema, EARS, RFC-2119, and cross-reference checks against
`docs/governance/TECHNICAL_CONSTITUTION.md`, `docs/governance/NFR_CATALOG.md`,
and `docs/governance/TEST_STRATEGY.md`.

Use before any phase transition (Phase 0 -> 1) or in CI as a gate.
