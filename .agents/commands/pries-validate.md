---
description: "PRIES validation gate for CI/CD: checks governance artefact compliance, NFR coverage, test pyramid ratios, and contract validation. Outputs PASS/FAIL with violations report."
agent: pries-pm
subtask: true
return:
  # Step 1: Validate Phase 0 governance artefacts.
  - /subtask {agent: pries-pm && as: val_governance} Run governance-validate-artifacts against docs/governance/. Block if errors > 0; warnings are advisory.

  # Step 2: NFR coverage of test strategy.
  - /subtask {agent: pries-pm && as: val_nfr_coverage} Cross-check that every NFR in docs/governance/NFR_CATALOG.md has a corresponding entry in docs/governance/TEST_STRATEGY.md. Report orphan NFRs and unreferenced strategies.

  # Step 3: Test pyramid ratios.
  - /subtask {agent: pries-pm && as: val_pyramid} Read TEST_STRATEGY.md pyramid ratios. Run a quick pytest collect to count tests by tier (unit / integration / e2e — by directory or marker). Report drift from declared ratios.

  # Step 4: Contract validation (NFR ID format, schema).
  - /subtask {agent: pries-pm && as: val_contracts} Verify NFR ID pattern (NFR-(PERF|REL|SEC|USE|MAIN|COMP|PORT|FUNC)-\\d{3}), priority enum (P0|P1|P2), EARS keywords in requirement statements, and acceptance criteria testability.

  # Step 5: Aggregate verdict.
  - /subtask {agent: pries-pm && as: val_aggregate} Combine $RESULT[val_governance], $RESULT[val_nfr_coverage], $RESULT[val_pyramid], $RESULT[val_contracts] into a unified report. Verdict = PASS if all step error counts == 0, else FAIL with violation list.

  # Step 6: Final summary.
  - "PRIES validation complete. See the unified report above. CI/CD systems should treat FAIL as a blocking exit code."
---
# PRIES Validate: $ARGUMENTS

Validation gate suitable for CI/CD pre-merge hooks. Confirms that the
repo meets PRIES + BMAD Phase 0 baselines:

1. **Governance artefacts present and valid** (constitution, NFR catalog,
   test strategy).
2. **NFR coverage** — every NFR has a test strategy entry.
3. **Test pyramid drift** — declared vs actual unit/integration/e2e ratios.
4. **Contract validation** — IDs, priorities, EARS keywords, testability.

## Exit semantics (for CI)

- Verdict `PASS` → exit 0.
- Verdict `FAIL` → exit non-zero with violation list on stderr.

## Use cases

- Pre-commit hook on `docs/governance/**` changes.
- Required check on PRs labelled `governance` or `feature`.
- Periodic drift check (cron).

## Recovery

- Missing artefact → `/governance-setup`.
- Schema violation → `/governance-update-constitution` or
  `/governance-add-nfr`.
- Pyramid drift → adjust `TEST_STRATEGY.md` or add tests.
