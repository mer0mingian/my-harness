---
description: "Phase 0: Technical Governance — produce TECHNICAL_CONSTITUTION.md, NFR_CATALOG.md, TEST_STRATEGY.md before BMAD Analysis."
agent: governance-lead
subtask: true
return:
  # 1. Discover existing repo signals before interviewing.
  - /subtask {agent: governance-lead && as: gov_discover} Scan the current repository for existing tech-stack signals — read CLAUDE.md, README.md, pyproject.toml, package.json, .editorconfig, docs/business/, docs/architecture/. Summarise what is already encoded so the interview only asks for the gaps.

  # 2. Conduct the interview using the governance-interview-tech-stack skill.
  - /subtask {agent: governance-lead && as: gov_interview} Using the gaps identified in $RESULT[gov_discover] and the governance-interview-tech-stack skill, run the structured interview for project "$ARGUMENTS". Return the structured YAML map (project, tech_stack, solution, security, nfr_priorities, test_strategy).

  # 3. Author all three artifacts in parallel.
  - /subtask {agent: governance-constitution-author && as: gov_constitution} Using $RESULT[gov_interview], generate docs/governance/TECHNICAL_CONSTITUTION.md per the governance-constitution-writer skill.
  - /subtask {agent: governance-nfr-specialist && as: gov_nfr} Using $RESULT[gov_interview], generate docs/governance/NFR_CATALOG.md per the governance-nfr-writer skill.
  - /subtask {agent: governance-test-architect && as: gov_test} Using $RESULT[gov_interview] and $RESULT[gov_nfr], generate docs/governance/TEST_STRATEGY.md per the governance-test-strategy-writer skill. Cross-reference NFR IDs.

  # 4. Validate the resulting artifacts.
  - /subtask {agent: governance-lead && as: gov_validate} Run the governance-validate-artifacts skill against docs/governance/. Report errors and warnings.

  # 5. User approval gate.
  - "Phase 0 (Technical Governance) for '$ARGUMENTS' is complete. Three artifacts are in docs/governance/. Validation report attached. Reply with 'Approved' to begin BMAD Phase 1 (Analysis) via /bmad-spec, or '/governance-update-constitution <section>' to amend a section first."
---
# Technical Governance Setup: $ARGUMENTS

Phase 0 of the BMAD workflow. The Governance Lead will scan the repo, interview
you on the gaps, then dispatch the Constitution Author, NFR Specialist, and Test
Architect in parallel. Outputs land in `docs/governance/` and are validated
before hand-off to BMAD Phase 1.
