---
name: governance-validate-artifacts
description: Validate Phase 0 governance artifacts (TECHNICAL_CONSTITUTION.md,
  NFR_CATALOG.md, TEST_STRATEGY.md) against JSON schemas, EARS syntax, RFC-2119
  discipline, and cross-reference integrity. Use before any phase transition or
  when /governance-validate is invoked.
---
# Governance Validate Artifacts

Lightweight, deterministic checks that any agent can run against the three
governance artifacts. Designed to fail fast with actionable messages.

## When to use

- After authoring or amending any governance artifact.
- Before transitioning from Phase 0 to BMAD Phase 1 (Analysis).
- When `/governance-validate` is invoked by the user.
- Inside CI pre-commit / pre-merge hooks.

## Files validated

| Path                                          | Schema                                                          |
| --------------------------------------------- | --------------------------------------------------------------- |
| `docs/governance/TECHNICAL_CONSTITUTION.md`   | `.agents/schemas/governance/constitution.schema.json`           |
| `docs/governance/NFR_CATALOG.md`              | `.agents/schemas/governance/nfr.schema.json`                    |
| `docs/governance/TEST_STRATEGY.md`            | `.agents/schemas/governance/test-strategy.schema.json`          |

## Check matrix

### Constitution checks

1. File exists and is non-empty.
2. All seven required headings present (`## 1. Technology Preferences` through
   `## 5. Amendment Process` and the Appendix).
3. Every `MUST` / `MUST NOT` line has an adjacent `Rationale:` or `TBD` marker.
4. Header contains `Version:`, `Last Updated:`, `Governance:` lines.
5. RFC-2119 keywords are uppercase.
6. Appendix tooling table has at least 5 rows (language, dep manager, linter,
   type checker, test runner).

### NFR catalog checks

1. File exists and is non-empty.
2. Every `### NFR-` block has: `**Category:**`, `**Requirement (EARS):**`,
   `**Acceptance Criteria:**`, `**Test Strategy:**`, `**Priority:**`.
3. The EARS line contains at least one of: `shall`, `when`, `while`, `where`,
   `if/then` (case-insensitive).
4. ID pattern matches `NFR-(PERF|REL|SEC|USE|MAIN|COMP|PORT|FUNC)-\d{3}`.
5. Priority is exactly one of `P0`, `P1`, `P2`.
6. NFR Validation Matrix appendix table has one row per NFR ID.
7. No duplicate IDs.

### Test strategy checks

1. File exists and is non-empty.
2. All nine required sections present.
3. Pyramid ratios sum to 100.
4. Every E2E journey row has ID matching `[A-Z]+-\d{3}` and a non-empty NFRs
   column (or explicit `none — reason: ...`).
5. Playwright section explicitly forbids `time.sleep` and mandates POM.
6. CI matrix has at least four trigger rows.
7. Coverage threshold matches the value in NFR-MAIN-001 (if present).

### Cross-reference checks

1. Every NFR ID referenced in TEST_STRATEGY exists in NFR_CATALOG.
2. Every constitution section referenced in NFR rationale exists.
3. Constitution `Coverage` rule (if present) and TEST_STRATEGY threshold agree.

## Reference implementation

See `.agents/skills/governance-validate-artifacts/scripts/validate.py` for a
Python implementation that runs without dependencies beyond `jsonschema` and
`pyyaml`. Agents may invoke it via `python -m governance.validate` or recreate
the same checks inline.

## Output format

Return a structured report. Example:

```yaml
overall: FAIL
errors:
  - file: docs/governance/NFR_CATALOG.md
    rule: ears_keyword_required
    location: "NFR-PERF-002"
    message: "Requirement statement contains no EARS keyword (shall/when/while/where/if-then)."
warnings:
  - file: docs/governance/TECHNICAL_CONSTITUTION.md
    rule: rationale_missing
    location: "Section 1.2 — 'MUST NOT use React'"
    message: "Rationale field empty; consider adding or marking TBD."
summary:
  constitution: { errors: 0, warnings: 1 }
  nfr: { errors: 1, warnings: 0 }
  test_strategy: { errors: 0, warnings: 0 }
```

## Anti-patterns

- Treating warnings as errors. Warnings are advisory; only errors block phase
  transition.
- Re-implementing the schema in prose. Always defer to the JSON schema files.
- Validating only the file the user just edited. Cross-references mean every
  validation run touches all three files.
